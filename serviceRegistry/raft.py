from threading import Timer
import random, os, requests, json

# raft states
LEADER = 'LEADER'
CANDIDATE = 'CANDIDATE'
FOLLOWER = 'FOLLOWER'

class Raft():
    def __init__(self, selfIP, partnerIPList, logger):
        self._logger = logger;
        self._selfIP = selfIP
        self._partnerIPList = partnerIPList
        self._data = {}
        # sample self._data = {
        #     "serverMap": {
        #         "127.0.0.1:2751": "1589819962.0",
        #         "27.0.0.1:2750": "1589819952.0"
        #     },
        #     "fileMap": {
        #         "50MB.avi": [
        #             {
        #                 "chunkNumber": 1,
        #                 "name": "348f95c89947ac4be76faabdcf660e65",
        #                 "size": 31457280
        #             },
        #             {
        #                 "chunkNumber": 2,
        #                 "name": "907e39b684bda5bfd0308f281628664c",
        #                 "size": 20257792
        #             }
        #         ]
        #     }
        # }

        self._term = 0
        self._state = FOLLOWER
        self._isLeader = False
        self._leaderIP = None
        self._candidacyTimer = None
        self._leaderTimer = None

        self._startCandidacyTimer()

    # set random candidacy timeout
    def _startCandidacyTimer(self):
        self._candidacyTimer = Timer(int(7 + random.random() * 4), self._startElection)
        self._candidacyTimer.daemon = True
        self._candidacyTimer.start()

    def _startElection(self):
        self._logger.info("%s starting election...", self._selfIP)
        self._state = CANDIDATE
        voteCount = 0
        for partnerIP in self._partnerIPList:
            try:
                params = { 'leaderIP': self._selfIP, 'term': self._term + 1 }
                raw_response = requests.get('http://' + partnerIP + "/raft/requestvote", params = params)
                obj = json.loads(raw_response.text)
                if obj['vote'] == True:
                    voteCount += 1
            except Exception as e:
                self._logger.warning("")
        if voteCount >= 1:
            self._logger.info("%s elected as leader", self._selfIP)
            self._term += 1
            self._declareLeaderAndStartHeartbeat()
        else:
            self._logger.info('election inconclusive, vote count: %s', voteCount)
            self._startCandidacyTimer()

    def _declareLeaderAndStartHeartbeat(self):
        self._logger.info("%s leader heartbeat...", self._selfIP)
        self._state = LEADER
        self._isLeader = True
        self._leaderIP = self._selfIP
        for partnerIP in self._partnerIPList:
            try:
                params = { 'leaderIP': self._selfIP, 'term': self._term }
                raw_response = requests.get('http://' + partnerIP + "/raft/heartbeat", params = params)
            except Exception as e:
                self._logger.warning("")
        self._leaderTimer = Timer(5, self._declareLeaderAndStartHeartbeat)
        self._leaderTimer.daemon = True
        self._leaderTimer.start()

    def _getCurrentDataFromLeaderOnStartup(self, leaderIP):
        try:
            raw_response = requests.get('http://' + leaderIP + "/raft/getcurrentdata")
            obj = json.loads(raw_response.text)
            self._data = obj['data']
            self._logger.info('self data: %s', self._data)
        except Exception as e:
            self._logger.warning("")

    # incoming request from a new follower, send the current data
    def getCurrentData(self):
        return self._data

    # incoming heartbeat form leader
    def ackLeaderHeartbeat(self, leaderIP, leaderTerm):
        if int(leaderTerm) >= int(self._term):
            self._state = FOLLOWER
            self._term = int(leaderTerm)
            self._isLeader = False
            if self._leaderIP is None:
                self._getCurrentDataFromLeaderOnStartup(leaderIP)
            self._leaderIP = leaderIP
            self._candidacyTimer.cancel()
            self._startCandidacyTimer()
            return True
        return False

    # incoming request from another node to become the new leader
    def voteRequested(self, newLeaderIP, newTerm):
        if int(newTerm) > int(self._term):
            self._state = FOLLOWER
            self._candidacyTimer.cancel()
            self._startCandidacyTimer()
            return True
        return False