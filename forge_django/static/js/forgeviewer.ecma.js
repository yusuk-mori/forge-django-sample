console.log("ecma loaded !!")

import VisualReportExtension from './Viewing.Extension.VisualReport/Viewing.Extension.VisualReport.js'

console.log("ecma loaded 2!!")

console.log(document)

export class MyForgeviewer {
    constructor()
    {
        console.log("MyForgeviewer constractor!!")

        //this.token = document.currentScript.getAttribute('token');
        //this.expires_in = document.currentScript.getAttribute('expires_in');

        //console.log("MyForgeviewer :" + this.token)
        //console.log("MyForgeviewer :" + this.expires_in)

        this.viewerApp=null;
        this.viewerElementId=null;

        var elm = document.getElementById("jstree")
        console.log(elm)

        document.getElementById("jstree").addEventListener("click", function(event){
            console.log('EventListener : click')
            console.log(event)

            //this.initializeViewer()
        });
    }

    initializeViewer(token, expired_sec, urn, elmid) {
        //DEBUG
        console.log("token       = " + token)
        console.log("urn         = " + urn)
        console.log("elmid       = " + elmid)
        console.log("expired_sec = " + expired_sec)

        viewerElementId = elmid

        var options = {
            env: 'AutodeskProduction',
            getAccessToken: function(onGetAccessToken) {
                var accessToken = token;
                var expireTimeSeconds = expired_sec;
                onGetAccessToken(accessToken, expireTimeSeconds);
            }

        };

        var base64urn = base64encode(urn)
        var documentId = "urn:" + base64urn;

        registerExtentions()

        var config3d = {
          extensions: ['VisualReportExtension']
        };

        Autodesk.Viewing.Initializer(options, function onInitialized(){
            this.viewerApp = new Autodesk.Viewing.ViewingApplication(viewerElementId);
            this.viewerApp.registerViewer(viewerApp.k3D, Autodesk.Viewing.Private.GuiViewer3D, config3d);
            this.viewerApp.loadDocument(documentId, onDocumentLoadSuccess, onDocumentLoadFailure);
        });

    }

}

console.log('const viewer !!');
const viewer = new MyForgeviewer();