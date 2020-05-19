import React from 'react';
import { Route, Switch } from 'react-router-dom';
import axios from 'axios';
import { ToastsStore, ToastsContainer, ToastsContainerPosition } from 'react-toasts';
import { MDBDataTable } from 'mdbreact';

var api_host = "http://localhost:5000";
class App extends React.Component {
  constructor(props) {
     super(props);
     this.state = {
       fileList: [],
       serverList: []
     }
  }
  componentDidMount() {
    this.getFiles();
    this.getServers();
  }

  render() {
    return (
      <div class="main-container">
        <h2 style={{textAlign:"center", marginBottom: "32px"}}>Dataverse</h2>
        <ul class="nav nav-tabs" id="myTab" role="tablist">
            <li class="nav-item">
              <a class="nav-link active" id="home-tab" data-toggle="tab" href="#home" role="tab" aria-controls="home" aria-selected="true">Upload</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" id="profile-tab" data-toggle="tab" href="#profile" role="tab" aria-controls="profile" aria-selected="false">Files</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" id="contact-tab" data-toggle="tab" href="#contact" role="tab" aria-controls="contact" aria-selected="false">Servers</a>
            </li>
          </ul>
          <div class="tab-content" id="myTabContent">
            <div class="tab-pane fade show active" id="home" role="tabpanel" aria-labelledby="home-tab">
                  <input id="file" name="file" type="file" onChange={(e) => this.setState({ file : e.target.files[0]})}/>
                  <button type="button" class="btn btn-primary" onClick={() =>  this.uploadFile()}>Upload</button>
            </div>
            <div class="tab-pane fade" id="profile" role="tabpanel" aria-labelledby="profile-tab">
                  <div className="d-flex justify-content-center">
                    <button type="button" class="btn btn-secondary" 
                       onClick={() => this.getFiles()}>Refresh</button>
                  </div>
                  <MDBDataTable
                    striped
                    bordered
                    dark
                    data={this.getFileTableOptions()}
                    style={{color: "white"}}/>
            </div>
            <div class="tab-pane fade" id="contact" role="tabpanel" aria-labelledby="contact-tab">
                  <div className="d-flex justify-content-center">
                      <button type="button" class="btn btn-secondary" 
                        onClick={() => this.getServers()}>Refresh</button>
                  </div>
                  <MDBDataTable
                    striped
                    bordered
                    dark
                    data={this.getServerTableOptions()}
                    style={{color: "white"}}/>
            </div>
          </div>
          <ToastsContainer store={ToastsStore} position={ToastsContainerPosition.BOTTOM_CENTER} />
      </div>
    );
  }
  uploadFile() {
       if(this.state.file) {
            var formData = new FormData();
            formData.append("file", this.state.file);
            axios.post(`${api_host}/upload`,formData,  {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })
            .then(resp => {
                ToastsStore.success(resp.data.msg);
            })
            .catch(err => {
                ToastsStore.warning("Error uploading file");
            });
       } else {
           ToastsStore.warning("please upload a file");
       }
  }
  getFiles() {
         axios.get(`${api_host}/getfilelist`)
         .then(resp => {
             ToastsStore.success("Fetched file list");
             let filelist = Object.keys(resp.data).map(x => {
                let obj = {};
                obj['filename'] = x;
                obj['size'] = 0
                resp.data[x].forEach(k =>  obj['size'] += k['size'])
                obj['action'] = (
                    <i class="fas fa-download"  onClick={ () => this.downloadFile(x)}></i>
                )
                return obj;
             })
             this.setState({
                fileList : filelist
             })
         })
         .catch(err => {
             ToastsStore.warning("Could not get file list");
         });
  }
  getServers() {
    axios.get(`${api_host}/getserverlist`)
    .then(resp => {
      ToastsStore.success("Fetched server list");
      let serverlist = Object.keys(resp.data).map(x => {
          let obj = {};
          let k = x.split(':');
          obj['host'] = k[0];
          obj['port'] = k[1];
          // resp.data[x].forEach(k =>  obj['size'] += k['size'])
          // obj['action'] = (
          //     <i class="fas fa-download"  onClick={ () => this.deleteFile(x)}></i>
          // )
          return obj;
      })
      this.setState({
          serverList : serverlist
      })
    })
    .catch(err => {
         ToastsStore.warning("Could not get server list");
    });
  }

  downloadFile(file) {
    ToastsStore.info("File will start downloading shortly");
    axios.get(`${api_host}/download`, {
      params : {
        filename : file
      }
    })
    .then(resp => {
      ToastsStore.info("File downloaded in " + resp.data.downloadtime.toFixed(2) + ' seconds');
    })
    .catch(err => {
         ToastsStore.warning("Could not get download file");
    });
  }
  getFileTableOptions(){
    var columns = [
      {
        label: 'File Name',
        field: 'filename',
        sort: 'asc',
      },
      {
        label: 'Size',
        field: 'size',
        sort: 'asc',
      },
      {
        label: 'Action',
        field: 'action',
      }
    ];
    return {
        columns: columns,
        rows: this.state.fileList
    } 
  }
  getServerTableOptions(){
    var columns = [
      {
        label: 'Server Host',
        field: 'host',
        sort: 'asc',
      },
      {
        label: 'Server Port',
        field: 'port',
        sort: 'asc',
      }
    ];
    return {
        columns: columns,
        rows: this.state.serverList
    } 
  }
}

export default App;
