
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
    console.log(this._viewer)
    console.log(this._viewer.model)

    //Set Event
    this._viewer.addEventListener(Autodesk.Viewing.SELECTION_CHANGED_EVENT, (item) =>{
        console.log('onSlectedItemChanged !!')
        console.log(item)
        //console.log(viewGeometryItem)
        var dbId = item.dbIdArray[0];
        console.log('dbId :' + dbId)

        this._viewer.getProperties(dbId, props => {
            props.properties.forEach(prop => {

                    var prop_name = prop.displayName + ((prop.type === 11) ? "[dbId]" : "");
                    var prop_value = prop.displayValue;
                    var prop_category = prop.displayCategory;

                    console.log(prop_name)
                    console.log(prop_value)
                    console.log(prop_category)
            });
        });
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