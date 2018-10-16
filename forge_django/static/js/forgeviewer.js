//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Copyright (c) Autodesk, Inc. All rights reserved
// Written by Yusuke Mori, Autodesk Consulting 2018
//
//   This software is provided as is, without any warranty that it will work. You choose to use this tool at your own risk.
//   Neither Autodesk nor the authors can be taken as responsible for any damage this tool can cause to
//   your data. Please always make a back up of your data prior to use this tool.
//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

var viewerApp;
//var viewer;
var viewerElementId


//=====================================================================================================================
// Viewer Initialization
//=====================================================================================================================
function initializeViewer(token, expired_sec, urn, elmid) {
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
      extensions: ['SelectEventExtension']
    };

    Autodesk.Viewing.Initializer(options, function onInitialized(){
        viewerApp = new Autodesk.Viewing.ViewingApplication(viewerElementId);
        viewerApp.registerViewer(viewerApp.k3D, Autodesk.Viewing.Private.GuiViewer3D, config3d);
        viewerApp.loadDocument(documentId, onDocumentLoadSuccess, onDocumentLoadFailure);
    });

}
//=====================================================================================================================
// Viewer Extension Common Module Framework
//=====================================================================================================================
/**
* Autodesk.Viewing.Document.load() success callback.
* Proceeds with model initialization.
*/
function onDocumentLoadSuccess(doc) {

    // We could still make use of Document.getSubItemsWithProperties()
    // However, when using a ViewingApplication, we have access to the **bubble** attribute,
    // which references the root node of a graph that wraps each object from the Manifest JSON.
    var viewables = viewerApp.bubble.search({'type':'geometry'});
    if (viewables.length === 0) {
        console.error('Document contains no viewables.');
        return;
    }

    // Choose any of the avialble viewables
    viewerApp.selectItem(viewables[0].data, onItemLoadSuccess, onItemLoadFail);

}

/**
 * Autodesk.Viewing.Document.load() failure callback.
 */
function onDocumentLoadFailure(viewerErrorCode) {
    console.error('onDocumentLoadFailure() - errorCode:' + viewerErrorCode);
}

function onItemLoadSuccess(viewer, item) {
    console.log('onItemLoadSuccess()!');
    // Congratulations! The viewer is now ready to be used.
    console.log('Viewers are equal: ' + (viewer === viewerApp.getCurrentViewer()));
}

function onItemLoadFail(errorCode) {
    console.error('onItemLoadFail() - errorCode:' + errorCode);
}
/**
 * BASE64 Utility
 */
function base64encode(str) {
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
 * extension register
 */
function registerExtentions(){

    Autodesk.Viewing.theExtensionManager.registerExtension('SelectEventExtension', SelectEventExtension);
}

//=====================================================================================================================
// Viewer Extension Core Definitions
//=====================================================================================================================
function SelectEventExtension(viewer, options) {
  Autodesk.Viewing.Extension.call(this, viewer, options);
}

SelectEventExtension.prototype = Object.create(Autodesk.Viewing.Extension.prototype);
SelectEventExtension.prototype.constructor = SelectEventExtension;

SelectEventExtension.prototype.load = function() {
    console.log('SelectEventExtension is loaded!');

    //Set Model Loaded Event
    this.viewer.addEventListener(Autodesk.Viewing.MODEL_ROOT_LOADED_EVENT, (item) => {
        console.log("Autodesk.Viewing.MODEL_ROOT_LOADED_EVENT !!")
        console.log(item);
        let wrapper = document.getElementById("forge-table-info_wrapper");
        if(null != wrapper) {
            //var container = document.getElementById("forge-table-info");
            let container = document.createElement('table');
            container.setAttribute("id", "forge-table-info");
            container.classList.add("table", "table-striped", "table-bordered");

            geom = item.model.getData();
            console.log(geom);

            var cbCount = 0; // count pending callbacks
            var components = []; // store the results
            var tree; // the instance tree

            function getLeafComponentsRec(current, parent) {
                cbCount++;
                let isfolder = false;
                if (tree.getChildCount(current) != 0) {
                    isfolder = true;
                    tree.enumNodeChildren(current, function (children) {
                        getLeafComponentsRec(children, current);
                    }, false);
                }

                if (null != parent){
                    parentname =  parent
                    if(true == isfolder)
                    {
                        iconname = "fa fa-folder"
                    }else {
                        iconname = "fa fa-file-o"
                    }
                }else{
                    parentname = "#"
                    iconname = "fa fa-archive"
                }

                let row = { 'id':current,'parent':parentname, 'text':tree.getNodeName(current), 'icon': iconname };
                components.push(row);


                if (--cbCount == 0) {
                    console.log("getLeafComponentsRec finished!!")
                    return components
                }
            }

            item.model.getObjectTree( (objectTree)=>{
                console.log("getObjectTree success!!")
                tree = objectTree;

                var allLeafComponents = getLeafComponentsRec(tree.getRootId(), null);
                console.log(allLeafComponents)
                console.log(typeof(allLeafComponents))
                //set tree
                console.log($('#jstree-objects').jstree(true).settings.core)
                $('#jstree-objects').jstree(true).settings.core.data = allLeafComponents;
                $('#jstree-objects').jstree(true).refresh();
            });

            console.log('creating DOM !!');
            //container.innerHTML = '';
            let infolist = {};
            // [MEMO] item type is Model.
            // See https://forge.autodesk.com/en/docs/viewer/v6/reference/javascript/model/
            infolist.geomPolyCount = item.model.geomPolyCount();
            infolist.RootId = item.model.getRootId();
            infolist.UnitScale = item.model.getUnitScale();
            infolist.UpVector = JSON.stringify(item.model.getUpVector());
            infolist.hasTopology = item.model.hasTopology();
            infolist.instancePolyCount = item.model.instancePolyCount();
            infolist.is3d = item.model.is3d();
            infolist.isAEC = item.model.isAEC();

            let doc = item.model.getDocumentNode();
            if (null != doc){
                infolist.Name = doc.name();
                infolist.PropertyDbPath = doc.findPropertyDbPath();
                infolist.PlacementTransform = doc.getPlacementTransform();
                infolist.Rootpath = doc.getViewableRootPath();
                infolist.guid = doc.guid();
                infolist.urn = doc.urn(true);
                infolist.tag = doc.getTag();
                infolist.isGeometry = doc.isGeometry();
                infolist.isGeomLeaf = doc.isGeomLeaf();
                infolist.isMetadata = doc.isMetadata();
            }

            let tr;
            let th;
            let td;

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

            //Reset current table wrapper
            let parent = wrapper.parentNode;
            parent.innerHTML = '';
            parent.appendChild(container);

            //[MEMO] Because of JQuery datatables.net sepcification,
            // To reset data table, it's necessary to remove parent warapper div element once.
            // This code is just tips for that.
            $("#forge-table-info").DataTable()

        }else{
            console.error('container not found !!')
        }
    });

    //Set Item Selected Event
    this.viewer.addEventListener(Autodesk.Viewing.SELECTION_CHANGED_EVENT, (item) =>{
        console.log('Autodesk.Viewing.SELECTION_CHANGED_EVENT !!');
        console.log(item);
        let wrapper = document.getElementById("forge-table-prop_wrapper");
        if (null != wrapper) {

            let dbId = item.dbIdArray[0];
            console.log('dbId :' + dbId);

            //var container = document.getElementById("forge-table-prop");
            //container.innerHTML = '';
            let container = document.createElement('table');
            container.setAttribute("id", "forge-table-prop");
            container.classList.add("table", "table-striped", "table-bordered");

            let tr;
            let th;
            let td;

            let thead = document.createElement('thead');

            tr = document.createElement('tr');

            th = document.createElement('th');
            th.innerHTML = "key";
            tr.appendChild(th);

            th = document.createElement('th');
            th.innerHTML = "value";
            tr.appendChild(th);

            th = document.createElement('th');
            th.innerHTML = "category";
            tr.appendChild(th);

            thead.appendChild(tr);

            this.viewer.getProperties(dbId, props => {
                //Iterate all propeties
                let tbody = document.createElement('tbody');
                let prop_key = null;
                let prop_value = null;
                let prop_category = null;

                props.properties.forEach(prop => {
                    prop_key = prop.displayName + ((prop.type === 11) ? "[dbId]" : "");
                    prop_value = prop.displayValue;
                    prop_category = prop.displayCategory;

                    //console.log(prop_key)
                    //console.log(prop_value)
                    //console.log(prop_category)

                    tr = document.createElement('tr');

                    td = document.createElement('td');
                    td.innerHTML = prop_key;
                    tr.appendChild(td);

                    td = document.createElement('td');
                    td.innerHTML = prop_value;
                    tr.appendChild(td);

                    td = document.createElement('td');
                    td.innerHTML = prop_category;
                    tr.appendChild(td);

                    tbody.appendChild(tr)
                });

                let children = tbody.childNodes;
                console.log(children)
                console.log(children.length)
                children.forEach(function (currentValue, currentIndex, listObj) {
                    console.log(currentValue)
                });

                container.appendChild(thead);
                container.appendChild(tbody);

                //Reset current table wrapper
                let parent = wrapper.parentNode;
                parent.innerHTML = '';
                parent.appendChild(container);

                //[MEMO] Because of JQuery datatables.net sepcification,
                // To reset data table, it's necessary to remove parent warapper div element once.
                // This code is just tips for that.
                $("#forge-table-prop").DataTable();
            })


        } else {
            console.error('container not found !!')
        }
    });

  return true;
};

SelectEventExtension.prototype.unload = function() {
  alert('MyAwesomeExtension is now unloaded!');
    this.viewer.toolbar.removeControl(this.subToolbar);
  return true;
};


SelectEventExtension.prototype.onToolbarCreated = function() {
  this.viewer.removeEventListener(av.TOOLBAR_CREATED_EVENT, this.onToolbarCreatedBinded);
  this.onToolbarCreatedBinded = null;
  this.createUI();
};

function getAlldbIds (rootId, treeitem) {
	var alldbId = [];
	if (!rootId) {
		return alldbId;
	}
	var queue = [];
	queue.push(rootId);
	while (queue.length > 0) {
		var node = queue.shift();
		alldbId.push(node);
		treeitem.enumNodeChildren(node, function(childrenIds) {
			queue.push(childrenIds);
		});
	}
	return alldbId;
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

    //const viewer = new MyForgeviewer();

    if(true == isAutheroized){
        console.log('switch to isAutheroized !!')
        // 6 create an instance when the DOM is ready
        //$('#jstree').jstree(treedata);
        jsTreeInitialize();
        closeReandeMeCollapse();

        // 7 bind to events triggered on the tree
        $('#jstree').on("changed.jstree", function (e, data) {
            if(data.selected && data.node) {
                console.log(data.selected);
                console.log(data.node.id);
                console.log(data.node.icon);
                if (data.node.icon.match(/fa-file-o/)) {
                    initializeViewer(token, expires_in, data.node.id, "forgeViewer")
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
            console.log('#hub-selecter change event : ' + $(this).val());
            showLoading();
            $.ajax({
                type: "GET",
                dataType: "json",
                url: "/api/forge/jstree-cache",
                cashe:false,
                data: { 'hubid' : $(this).val()},
            }).done(function(result) {
                console.log(result);

                if (result['error']){
                    console.log('/api/forge/jstree-cache return nothing.')
                    //[MEMO] If there is not DB cache data yet, user can start fetch all command.
                    //show "fetch all" button
                    showFetchButton();
                    //Set #jstree default data
                    jsTreeSetDefault();
                }else{
                    hideFetchButton();
                    $('#jstree').jstree(true).settings.core.data = result.core.data;
                    $('#jstree').jstree(true).refresh();
                }

            }).fail(function( jqXHR, textStatus, errorThrown ) {
                console.log(jqXHR)
                console.log(textStatus)
                console.log(errorThrown)
                alert(textStatus);
            }).always(function(){
                hideLoading();
                jsTreeObjectsSetDefault();
                resetTableProp();
                resetTableInfo();
            });
        });

        $('#logout-btn').on('click', function () {
            showLoading();
            console.log("#token-btn click!!")
            location.href = '/api/forge/reset/'
        });

    }else{
        jsTreeSetDefault();
        jsTreeObjectsSetDefault();

        $('#login-btn').on('click', function () {
            console.log("#token-btn click!!");
            showLoading();
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
                //alert(textStatus);
            }).always(function(){
                //hideLoading();
            });
        });
    }

    //Always set these event callback
    $('#fetch-btn').on('click', function () {
        console.log("#fetch-btn click!!")
        showLoading();
        $.ajax({
            type: "GET",
            dataType: "json",
            url: "/api/forge/jstree",
            cashe:false,
            data: { 'hubid' : $("#hub-selecter").val()},
        }).done(function(result) {
            console.log(result)
            $('#jstree').jstree(true).settings.core.data = result.core.data;
            $('#jstree').jstree(true).refresh();
            hideFetchButton();
        }).fail(function( jqXHR, textStatus, errorThrown ) {
            console.log(jqXHR)
            console.log(textStatus)
            console.log(errorThrown)
            //alert(textStatus);
        }).always(function () {
            hideLoading();
        });
    });

    hideLoading();
});

function jsTreeInitialize() {
    var selecter = $("#hub-selecter");
    console.log(selecter)
    if (selecter != null) {
        console.log('index : ' + selecter.get(0).selectedIndex)
        console.log('value : ' + selecter.get(0).value)
        showLoading();
        $.ajax({
            type: "GET",
            dataType: "json",
            url: "/api/forge/jstree-cache",
            cashe: false,
            data: {'hubid': selecter.get(0).value},
        }).done(function (result) {
            if (result['error']){
                //[MEMO] If there is not DB cache data yet, user can start fetch all command.
                //show "fetch all" button
                showFetchButton();
                //Set #jstree default data
                jsTreeSetDefault();

            }else{
                //This is first time initialization
                $('#jstree').jstree(result)
            }
        }).fail(function (result) {
            alert('error!!!');
        }).always(function () {
            hideLoading();
        });
    }

    // set #jstree-objects default data
    jsTreeObjectsSetDefault();
}

function jsTreeSetDefault() {
        //set default empty data set and initialize jstree
        let defaultdata = {}
        defaultdata["core"] = {}
        defaultdata["core"]["data"] = [{"id":1000, "parent" :"#", "text":"No Hub Site Fetched Yet", "icon":"fa fa-warning" }]
        if( null != $('#jstree').jstree(true).settings) {
            $('#jstree').jstree(true).settings.core.data = defaultdata.core.data;
            $('#jstree').jstree(true).refresh();
        }else {
            $('#jstree').jstree(defaultdata)
        }
}

function jsTreeObjectsSetDefault() {
    let defaultdata = {}
    defaultdata["core"] = {}
    defaultdata["core"]["data"] = [{"id":1000, "parent" :"#", "text":"No Model Selected", "icon":"fa fa-warning" }]
    if( null != $('#jstree-objects').jstree(true).settings) {
        $('#jstree-objects').jstree(true).settings.core.data = defaultdata.core.data;
        $('#jstree-objects').jstree(true).refresh();
    }else {
        $('#jstree-objects').jstree(defaultdata);
    }
}

function hideLoading(){
    $( "#loading" ).fadeOut("slow");
    $( "#loading" ).addClass("is-hide");
}

function showLoading(){
    $( "#loading" ).fadeIn("slow");
    $( "#loading" ).removeClass("is-hide");
}

function hideFetchButton(){
    $( "#fetch-btn" ).fadeOut("slow");
    $( "#fetch-btn" ).addClass("is-hide");
}

function showFetchButton(){
    $( "#fetch-btn" ).fadeIn("slow");
    $( "#fetch-btn" ).removeClass("is-hide");
}

function resetTableBase(idname, threads){
    let wrapper = document.getElementById(idname + "_wrapper");
    if (null != wrapper) {
        let parent = wrapper.parentNode;
        let container = document.createElement('table');
        container.setAttribute("id", idname);
        container.classList.add("table", "table-striped", "table-bordered");

        let tr;
        let th;
        let td;

        let thead = document.createElement('thead');

        tr = document.createElement('tr');

        threads.forEach(function(itr){
            th = document.createElement('th');
            th.innerHTML = itr;
            tr.appendChild(th);
        });

        thead.appendChild(tr);
        container.appendChild(thead);

        let tbody = document.createElement('tbody');
        container.appendChild(tbody);

        parent.innerHTML = '';
        parent.appendChild(container);
        $("#"+idname).DataTable();
    }
}

function resetTableProp() {
    resetTableBase("forge-table-prop", ["key", "value",  "category"]);
}

function resetTableInfo(){
    resetTableBase("forge-table-info",  ["key", "value"]);
}

function closeReandeMeCollapse() {
    let collapse = document.getElementById("readme-collapse")
    if (null != collapse){
        collapse.click()
    }
}