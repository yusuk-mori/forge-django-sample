console.log(location.pathname + " : loaded !!")


console.log("try import")
//import VisualReportExtension from './Viewing.Extension.VisualReport/Viewing.Extension.VisualReport.js'
import ExtensionSelectEvent from './forgeviewer.Extension.SelectEvent.js'

console.log("passed import")

//=====================================================================================================================
// Global variables
//=====================================================================================================================
var viewerApp = null


//=====================================================================================================================
// Class Declare
//=====================================================================================================================
class MyForgeviewer {
    constructor(token, expires_in)
    {
        console.log("MyForgeviewer constractor!!")
    }

    initializeViewer(token, expired_sec, urn, elmid) {
        //DEBUG
        console.log("token       = " + token)
        console.log("urn         = " + urn)
        console.log("elmid       = " + elmid)
        console.log("expired_sec = " + expired_sec)


        var viewerElementId = elmid

        var options = {
            env: 'AutodeskProduction',
            getAccessToken: function(onGetAccessToken) {
                var accessToken = token;
                var expireTimeSeconds = expired_sec;
                onGetAccessToken(accessToken, expireTimeSeconds);
            }

        };

        var base64urn = this.base64encode(urn)
        var documentId = "urn:" + base64urn;

        this.registerExtentions();

        var config3d = {
          extensions: ['ExtensionSelectEvent']
        };

        Autodesk.Viewing.Initializer(options, this.onInitialized(viewerElementId, documentId, config3d));

    }

    onInitialized(viewerElementId, documentId, config3d){
            viewerApp = new Autodesk.Viewing.ViewingApplication(viewerElementId);
            viewerApp.registerViewer(viewerApp.k3D, Autodesk.Viewing.Private.GuiViewer3D, config3d);

            //Set Event
            viewerApp.addItemSelectedObserver(MyForgeviewer.onItemSelected);

            viewerApp.loadDocument(documentId, this.onDocumentLoadSuccess, this.onDocumentLoadFailure);
    }


    base64encode(str) {
        var ret = "";
        if (window.btoa) {
            ret = window.btoa(str);
        } else {
            // IE9 support
            ret = window.Base64.encode(str);
        }

        // Remove ending '=' signs
        // Use _ instead of /
        // Use - insteaqd of +
        // Have a look at this page for info on "Unpadded 'base64url' for "named information" URI's (RFC 6920)"
        // which is the format being used by the Model Derivative API
        // https://en.wikipedia.org/wiki/Base64#Variants_summary_table
        var ret2 = ret.replace(/=/g, '').replace(/[/]/g, '_').replace(/[+]/g, '-');

        console.log('base64encode result = ' + ret2);

        return ret2;
    }


    /**
    * Autodesk.Viewing.Document.load() success callback.
    * Proceeds with model initialization.
    */
    onDocumentLoadSuccess(doc) {
        console.log('onDocumentLoadSuccess()!!')

        // We could still make use of Document.getSubItemsWithProperties()
        // However, when using a ViewingApplication, we have access to the **bubble** attribute,
        // which references the root node of a graph that wraps each object from the Manifest JSON.
        var viewables = viewerApp.bubble.search({'type':'geometry'});
        if (viewables.length === 0) {
            console.error('Document contains no viewables.');
            return;
        }

        // Choose any of the avialble viewables
        viewerApp.selectItem(viewables[0].data, MyForgeviewer.onItemLoadSuccess, MyForgeviewer.onItemLoadFail);
    }


    /**
     * Autodesk.Viewing.Document.load() failure callback.
     */
    onDocumentLoadFailure(viewerErrorCode) {
        console.error('onDocumentLoadFailure() - errorCode:' + viewerErrorCode);
    }

    static onItemLoadSuccess(viewer, item) {
        console.log('onItemLoadSuccess()!');
        // Congratulations! The viewer is now ready to be used.
        console.log('Viewers are equal: ' + (viewer === viewerApp.getCurrentViewer()));
    }

    static onItemLoadFail(errorCode) {
        console.error('onItemLoadFail() - errorCode:' + errorCode);
    }

    registerExtentions(){

        Autodesk.Viewing.theExtensionManager.registerExtension('ExtensionSelectEvent', ExtensionSelectEvent);
        //Autodesk.Viewing.theExtensionManager.registerExtension('VisualReportExtension', VisualReportExtension);
    }

    static addInformationTable(item){
        console.log('addInformationTable !!');
        var wrapper = document.getElementById("forge-table-info_wrapper");
        var parent = wrapper.parentNode

        //var container = document.getElementById("forge-table-info");
        var container = document.createElement('table');
        container.setAttribute("id", "forge-table-info");
        container.classList.add("table", "table-striped", "table-bordered");

        if(null != wrapper) {
            console.log('creating DOM !!');
            //container.innerHTML = '';
            let infolist = {};
            // [MEMO] item type is BubbleNode.
            // See https://forge.autodesk.com/en/docs/viewer/v6/reference/javascript/bubblenode/
            infolist.Name = item.name();
            infolist.PropertyDbPath = item.findPropertyDbPath();
            infolist.PlacementTransform = item.getPlacementTransform();
            infolist.Rootpath = item.getViewableRootPath();
            infolist.guid = item.guid();
            infolist.urn = item.urn(true);
            infolist.tag = item.getTag();
            infolist.isGeometry = item.isGeometry();
            infolist.isGeomLeaf = item.isGeomLeaf();
            infolist.isMetadata = item.isMetadata();

            let tr = null;
            let th = null;
            let td = null;

            let thead = document.createElement('thead');

            tr = document.createElement('tr');

            th = document.createElement('th');
            th.innerHTML = "key";
            tr.appendChild(th);

            th = document.createElement('th');
            th.innerHTML = "value";
            tr.appendChild(th);

            thead.appendChild(tr);

            let tbody = document.createElement('tbody');

            for( let key in infolist){

                tr = document.createElement('tr');

                th = document.createElement('th');
                th.innerHTML = key;
                tr.appendChild(th);

                td = document.createElement('td');
                td.innerHTML = infolist[key];
                tr.appendChild(td)

                tbody.appendChild(tr)
            }

            container.appendChild(thead);
            container.appendChild(tbody);

            //[MEMO] Because of JQuery datatables.net sepcification,
            // To reset data table, it's necessary to remove parent warapper div element once.
            // This code is just tips for that.
            wrapper.remove();
            parent.appendChild(container);
            // Reset dynamic data table widgets
            //init_DataTables();
            init_SingleDataTables("#forge-table-info");

        }else{
            console.error('container not found !!')
        }
    }

}

//=====================================================================================================================
// Document on load event
//=====================================================================================================================
$(function () {
    console.log('Viewer initialization on Document loaded event ...');

    var token = $("#forgeviewer-script").attr('token')
    var expires_in = $("#forgeviewer-script").attr('expires_in')

    // cast attribute string "true" or "false" to boolean
    var isAutheroized = "True" == ($("#forgeviewer-script").attr('is_auth')) ? true : false;

    console.log(token)
    console.log(expires_in)
    console.log(typeof(isAutheroized))

    const viewer = new MyForgeviewer();

    if(true == isAutheroized){
        console.log('switch to isAutheroized !!')
        // 6 create an instance when the DOM is ready
        //$('#jstree').jstree(treedata);
        jsTreeInitialize()

        // 7 bind to events triggered on the tree
        $('#jstree').on("changed.jstree", function (e, data) {
            if(data.selected && data.node) {
                console.log(data.selected);
                console.log(data.node.id);
                console.log(data.node.icon);
                if ('jstree-file' == data.node.icon) {
                    viewer.initializeViewer(token, expires_in, data.node.id, "forgeViewer")
                }
            }
        });
        // 8 interact with the tree - either way is OK
        $('button').on('click', function () {
          $('#jstree').jstree(true).select_node('child_node_1');
          $('#jstree').jstree('select_node', 'child_node_1');
          $.jstree.reference('#jstree').select_node('child_node_1');
        });

        //set hub-selecter event hanlder
        $("#hub-selecter").change(function(){
            console.log('#hub-selecter change event : ' + $(this).val())
            $.ajax({
                type: "GET",
                dataType: "json",
                url: "/api/forge/jstree",
                cashe:false,
                data: { 'hubid' : $(this).val()},
            }).done(function(result) {
                console.log(result);
                $('#jstree').jstree(true).settings.core.data = result.core.data;
                $('#jstree').jstree(true).refresh();
            }).fail(function(result) {
                alert('error!!!');
            });
        });

        $('#logout-btn').on('click', function () {

            console.log("#token-btn click!!")
            location.href = '/api/forge/reset/'
        });

    }else{
        $('#login-btn').on('click', function () {
            console.log("#token-btn click!!")
            $.ajax({
                type: "GET",
                dataType: "text",
                url: "/api/forge/gettoken",
                headers : {
                    'Access-Control-Allow-Origin': 'http://127.0.0.1:8000',
                    'Access-Control-Allow-Methods':'GET, POST, OPTIONS',
                },
                cashe:false,
            }).done(function(redirecturl) {
                console.log(redirecturl)
                location.href = redirecturl;

            }).fail(function( jqXHR, textStatus, errorThrown ) {
                console.log(jqXHR)
                console.log(textStatus)
                console.log(errorThrown)
                alert(textStatus);
            });
        });
    }
});

function jsTreeInitialize() {
    var selecter = $("#hub-selecter");
    console.log(selecter)
    if (selecter != null) {
        console.log('index : ' + selecter.get(0).selectedIndex)
        console.log('value : ' + selecter.get(0).value)
        $.ajax({
            type: "GET",
            dataType: "json",
            url: "/api/forge/jstree",
            cashe: false,
            data: {'hubid': selecter.get(0).value},
        }).done(function (result) {
            //console.log(result);
            //This is first time initialization
            $('#jstree').jstree(result)

        }).fail(function (result) {
            alert('error!!!');
        });
    }
}