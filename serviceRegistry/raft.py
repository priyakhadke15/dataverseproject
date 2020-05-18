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

        self._term = 1
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
            self._declareLeaderAndStartHeartbeat()
        else:
            self._logger.info('election inconclusive, vote count: %s', voteCount)
            self._startCandidacyTimer()

    def _declareLeaderAndStartHeartbeat(self):
        self._logger.info("%s leader heartbeat...", self._selfIP)
        self._state = LEADER
        self._term += 1
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

    # incoming heartbeat form leader
    def ackLeaderHeartbeat(self, leaderIP, leaderTerm):
        if int(leaderTerm) >= int(self._term):
            self._state = FOLLOWER
            self._term = int(leaderTerm)
            self._isLeader = False
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