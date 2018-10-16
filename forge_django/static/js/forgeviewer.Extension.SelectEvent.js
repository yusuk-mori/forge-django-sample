//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Copyright (c) Autodesk, Inc. All rights reserved
// Written by Yusuke Mori, Autodesk Consulting 2018
//
//   This software is provided as is, without any warranty that it will work. You choose to use this tool at your own risk.
//   Neither Autodesk nor the authors can be taken as responsible for any damage this tool can cause to
//   your data. Please always make a back up of your data prior to use this tool.
//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

import ExtensionBase from './components/Viewer.ExtensionBase/Viewer.ExtensionBase.js'

export default class ExtensionSelectEvent extends ExtensionBase {

  /////////////////////////////////////////////////////////////////
  // Class constructor
  //
  /////////////////////////////////////////////////////////////////
  constructor (viewer, options = {}) {
    console.log('ExtensionSelectEvent constructor !!')
    super (viewer, options)
  }

  /////////////////////////////////////////////////////////////////
  // Extension Id
  //
  /////////////////////////////////////////////////////////////////
  static get ExtensionId() {

    return 'forgeviewer.Extension.SelectEvent'
  }

  /////////////////////////////////////////////////////////////////
  // Load callback
  //
  /////////////////////////////////////////////////////////////////
  load() {

    console.log('ExtensionSelectEvent load() !!')
    //console.log(this._viewer);

    //Set Model Loaded Event
    this._viewer.addEventListener(Autodesk.Viewing.MODEL_ROOT_LOADED_EVENT, (item) => {
        console.log("Autodesk.Viewing.MODEL_ROOT_LOADED_EVENT !!")
        console.log(item)
        var wrapper = document.getElementById("forge-table-info_wrapper");
        if(null != wrapper) {
            //var container = document.getElementById("forge-table-info");
            var container = document.createElement('table');
            container.setAttribute("id", "forge-table-info");
            container.classList.add("table", "table-striped", "table-bordered");

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

            //Reset current table wrapper
            var parent = wrapper.parentNode;
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
    this._viewer.addEventListener(Autodesk.Viewing.SELECTION_CHANGED_EVENT, (item) =>{
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

            th = document.createElement('th');
            th.innerHTML = "type";
            tr.appendChild(th);

            thead.appendChild(tr);

            this._viewer.getProperties(dbId, props => {
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

                var children = tbody.childNodes;
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

    return true
  }

  /////////////////////////////////////////////////////////////////
  // Unload callback
  //
  /////////////////////////////////////////////////////////////////
  unload() {

    return true
  }

}