
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
    this._viewer.addEventListener(Autodesk.Viewing.SELECTION_CHANGED_EVENT, this.onItemSelected)

    return true
  }

  /////////////////////////////////////////////////////////////////
  // Unload callback
  //
  /////////////////////////////////////////////////////////////////
  unload() {

    return true
  }


  onItemSelected(item,viewGeometryItem){
        console.log('onSlectedItemChanged !!')
        console.log(item)
        console.log(viewGeometryItem)
  }
}