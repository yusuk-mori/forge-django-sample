
var viewerApp;
//var viewer;
var viewerElementId



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
      extensions: ['SampleExtension']
    };

    Autodesk.Viewing.Initializer(options, function onInitialized(){
        viewerApp = new Autodesk.Viewing.ViewingApplication(viewerElementId);
        viewerApp.registerViewer(viewerApp.k3D, Autodesk.Viewing.Private.GuiViewer3D, config3d);
        viewerApp.loadDocument(documentId, onDocumentLoadSuccess, onDocumentLoadFailure);
    });

}

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
    console.log(viewer);
    console.log(item);

    // Congratulations! The viewer is now ready to be used.
    console.log('Viewers are equal: ' + (viewer === viewerApp.getCurrentViewer()));
}

function onItemLoadFail(errorCode) {
    console.error('onItemLoadFail() - errorCode:' + errorCode);
}

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

function registerExtentions(){

    Autodesk.Viewing.theExtensionManager.registerExtension('SampleExtension', SampleExtension);
    //Autodesk.Viewing.theExtensionManager.registerExtension('VisualReportExtension', VisualReportExtension);
}

function SampleExtension(viewer, options) {
  Autodesk.Viewing.Extension.call(this, viewer, options);
}

SampleExtension.prototype = Object.create(Autodesk.Viewing.Extension.prototype);
SampleExtension.prototype.constructor = SampleExtension;

SampleExtension.prototype.load = function() {
  alert('SampleExtension is loaded!');

  if (this.viewer.toolbar) {
    // Toolbar is already available, create the UI
    this.createUI();
  } else {
    // Toolbar hasn't been created yet, wait until we get notification of its creation
    this.onToolbarCreatedBinded = this.onToolbarCreated.bind(this);
    this.viewer.addEventListener(av.TOOLBAR_CREATED_EVENT, this.onToolbarCreatedBinded);
  }

  return true;
};

SampleExtension.prototype.unload = function() {
  alert('MyAwesomeExtension is now unloaded!');
    this.viewer.toolbar.removeControl(this.subToolbar);
  return true;
};


SampleExtension.prototype.onToolbarCreated = function() {
  this.viewer.removeEventListener(av.TOOLBAR_CREATED_EVENT, this.onToolbarCreatedBinded);
  this.onToolbarCreatedBinded = null;
  this.createUI();
};

SampleExtension.prototype.createUI = function() {
  alert('TODO: Create Toolbar!');

  var viewer = this.viewer;

  // Button 1
  var button1 = new Autodesk.Viewing.UI.Button('my-view-front-button');
  button1.onClick = function(e) {
      viewer.setViewCube('front');
  };
  button1.addClass('fa-adn');
  button1.setToolTip('View front');

  // Button 2
  var button2 = new Autodesk.Viewing.UI.Button('my-view-back-button');
  button2.onClick = function(e) {
      viewer.setViewCube('back');
  };
  button2.addClass('fa-adn');
  button2.setToolTip('View Back');

  // SubToolbar
  this.subToolbar = new Autodesk.Viewing.UI.ControlGroup('my-custom-view-toolbar');
  this.subToolbar.addControl(button1);
  this.subToolbar.addControl(button2);

  viewer.toolbar.addControl(this.subToolbar);
};
