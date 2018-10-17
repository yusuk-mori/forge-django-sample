//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Copyright (c) Autodesk, Inc. All rights reserved
// Written by Yusuke Mori, Autodesk Consulting 2018
//
//   This software is provided as is, without any warranty that it will work. You choose to use this tool at your own risk.
//   Neither Autodesk nor the authors can be taken as responsible for any damage this tool can cause to
//   your data. Please always make a back up of your data prior to use this tool.
//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//=====================================================================================================================
// Viewer Extension Core Definitions
//=====================================================================================================================
function ChartsExtension(viewer, options) {
  Autodesk.Viewing.Extension.call(this, viewer, options);
}

ChartsExtension.prototype = Object.create(Autodesk.Viewing.Extension.prototype);
ChartsExtension.prototype.constructor = ChartsExtension;

ChartsExtension.prototype.load = function() {
    console.log('ChartsExtension is loaded!');

    //Set Model Loaded Event
    this.viewer.addEventListener(Autodesk.Viewing.MODEL_ROOT_LOADED_EVENT, (item) => {
        console.log("Autodesk.Viewing.MODEL_ROOT_LOADED_EVENT (2) !!")

        showAllNodataIcon();

        let chart = document.getElementById("chart-category");
        if(null != chart) {

            geom = item.model.getData();
            //console.log(geom);

            let cbCount = 0; // count pending callbacks
            let nodelist = []; // store all nodes which has category property.
            let tree; // the instance tree

            function getLeafComponentsRec(current, parent) {
                let self = this;

                cbCount++;
                let isfolder = false;
                if (tree.getChildCount(current) != 0) {
                    isfolder = true;
                    tree.enumNodeChildren(current, function (children) {
                        getLeafComponentsRec(children, current);
                    }, false);
                }

                nodelist.push({"id":current});

                if (--cbCount == 0) {
                    console.log("getLeafComponentsRec finished!!")
                    return nodelist
                }
            }

            item.model.getObjectTree((objectTree) => {
                console.log("getObjectTree success!!")
                tree = objectTree;

                //console.log(tree);

                let allNodeList = getLeafComponentsRec(tree.getRootId(), null);
                //console.log(allNodeList);

                let self = this;
                let catgorylist = []; // store the results
                let walllist = []; // only wall list
                let floorlist = []; // only floor list
                let ceillist = []; // only Ceiling list

                //Create Promise List
                //[MEMO] "this.viewer.getProperties" callback is async,
                // then, chart graph is need to be render after all callback is done..
                let promises = [];

                allNodeList.forEach( (itr)=>{
                    promises.push( new Promise( (resolve, reject) => {
                        this.viewer.getProperties(itr.id, props => {
                            //console.log(props);
                            let curcatgory="";
                            props.properties.some((prop, index) => {
                                if ("Category" == prop.displayName) {
                                    curcatgory = prop.displayValue;
                                    let row = {'id': itr.id, 'value': prop.displayValue};
                                    catgorylist.push(row);
                                    return true;
                                }
                            });
                            console.log("curcatgory : " + curcatgory)
                            //At this moment, Only en/ja category name matching. Sorry for hard cording.
                            if (null != curcatgory.match(/Revit (Walls|壁)/)){
                                console.log("wall match!!");

                                //Get Material Property
                                props.properties.some((prop, index) => {
                                    if (null != prop.displayName.match(/Structural Material|構造マテリアル/)) {

                                        let row = {'id': itr.id, 'value': (("" != prop.displayValue) ? prop.displayValue : "undefined")  };
                                        walllist.push(row);
                                        return true;
                                    }
                                });
                            }

                            if (null != curcatgory.match(/Revit (Floors|床)/)){
                                console.log("floor match!!");

                                //Get Material Property
                                props.properties.some((prop, index) => {
                                    if (null != prop.displayName.match(/Structural Material|構造マテリアル/)) {
                                        let row = {'id': itr.id, 'value': (("" != prop.displayValue) ? prop.displayValue : "undefined")};
                                        floorlist.push(row);
                                        return true;
                                    }
                                });
                            }

                            if (null != curcatgory.match(/Revit (Ceilings|天井)/)){
                                console.log("floor match!!");
                                let volume=0;
                                let area=0;

                                //Get Material Property
                                props.properties.some((prop, index) => {
                                    if (null != prop.displayName.match(/Perimeter|周長/)) {
                                       volume = ("" != prop.displayValue) ? parseFloat(prop.displayValue) : 0;
                                        return true;
                                    }
                                });

                                props.properties.some((prop, index) => {
                                    if (null != prop.displayName.match(/Area|面積/)) {
                                       area = ("" != prop.displayValue) ? parseFloat(prop.displayValue) : 0;
                                        return true;
                                    }
                                });

                                let row = [ volume, area ];
                                ceillist.push(row);
                            }

                            resolve(catgorylist);
                        });
                    }));
                });

                Promise.all(promises).then( (results) =>{
                    console.log("all then !!");
                    //console.log(catgorylist);
                    //console.log(walllist);
                    //console.log(floorlist);
                    console.log(ceillist);

                    //set tree
                    let statistic = parseChartData(catgorylist);
                    console.log(statistic);
                    if(statistic.length > 0) {
                        hideNodataIcon("chart-category");
                        setChartDonutData("chart-category", statistic);
                    }

                    statistic = parseChartData(walllist);
                    console.log(statistic);
                    if(statistic.length > 0) {
                        hideNodataIcon("chart-wall");
                        setChartDonutData("chart-wall", statistic);
                    }

                    statistic = parseChartData(floorlist);
                    console.log(statistic);
                    if(statistic.length > 0) {
                        hideNodataIcon("chart-floor");
                        setChartDonutData("chart-floor", statistic);
                    }

                    if(ceillist.length > 0){
                        hideNodataIcon("chart-ceiling");
                        setScatterCharts("chart-ceiling", ceillist);
                    }
                });

            });

        }else{
            console.error('chart-category  not found !!')
        }
    });

    return true;
};

ChartsExtension.prototype.unload = function() {
  alert('MyAwesomeExtension is now unloaded!');
    this.viewer.toolbar.removeControl(this.subToolbar);
  return true;
};

ChartsExtension.prototype.onToolbarCreated = function() {
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

    console.log(token);
    console.log(expires_in);
    console.log(isAutheroized);

    if(true == isAutheroized){
        console.log('switch to isAutheroized !!')
    }else {

    }
});



function hideLoading(){
    $( "#loading" ).fadeOut("slow");
    $( "#loading" ).addClass("is-hide");
}

function showLoading(){
    $( "#loading" ).fadeIn("slow");
    $( "#loading" ).removeClass("is-hide");
}

function hideNodataIcon(idname){
    $( "#" + idname + "-nodata" ).fadeOut("slow");
    $( "#" + idname).fadeIn("slow");
}

function showNodataIcon(idname){
    $( "#" + idname).fadeOut("slow");
    $( "#" + idname + "-nodata" ).fadeIn("slow");
}

function showAllNodataIcon(){
    showNodataIcon("chart-category");
    showNodataIcon("chart-wall");
    showNodataIcon("chart-floor");
    showNodataIcon("chart-ceiling");
}

//=====================================================================================================================
// Chart Drawing
//=====================================================================================================================
const theme = {
    color: [
        '#26B99A', '#34495E', '#BDC3C7', '#3498DB',
        '#9B59B6', '#8abb6f', '#759c6a', '#bfd3b7'
    ],

    title: {
        itemGap: 8,
        textStyle: {
            fontWeight: 'normal',
            color: '#408829'
        }
    },

    dataRange: {
        color: ['#1f610a', '#97b58d']
    },

    toolbox: {
        color: ['#408829', '#408829', '#408829', '#408829']
    },

    tooltip: {
        backgroundColor: 'rgba(0,0,0,0.5)',
        axisPointer: {
            type: 'line',
            lineStyle: {
                color: '#408829',
                type: 'dashed'
            },
            crossStyle: {
                color: '#408829'
            },
            shadowStyle: {
                color: 'rgba(200,200,200,0.3)'
            }
        }
    },

    dataZoom: {
        dataBackgroundColor: '#eee',
        fillerColor: 'rgba(64,136,41,0.2)',
        handleColor: '#408829'
    },
    grid: {
        borderWidth: 0
    },

    categoryAxis: {
        axisLine: {
            lineStyle: {
                color: '#408829'
            }
        },
        splitLine: {
            lineStyle: {
                color: ['#eee']
            }
        }
    },

    valueAxis: {
        axisLine: {
            lineStyle: {
                color: '#408829'
            }
        },
        splitArea: {
            show: true,
            areaStyle: {
                color: ['rgba(250,250,250,0.1)', 'rgba(200,200,200,0.1)']
            }
        },
        splitLine: {
            lineStyle: {
                color: ['#eee']
            }
        }
    },
    timeline: {
        lineStyle: {
            color: '#408829'
        },
        controlStyle: {
            normal: { color: '#408829' },
            emphasis: { color: '#408829' }
        }
    },

    k: {
        itemStyle: {
            normal: {
                color: '#68a54a',
                color0: '#a9cba2',
                lineStyle: {
                    width: 1,
                    color: '#408829',
                    color0: '#86b379'
                }
            }
        }
    },
    map: {
        itemStyle: {
            normal: {
                areaStyle: {
                    color: '#ddd'
                },
                label: {
                    textStyle: {
                        color: '#c12e34'
                    }
                }
            },
            emphasis: {
                areaStyle: {
                    color: '#99d2dd'
                },
                label: {
                    textStyle: {
                        color: '#c12e34'
                    }
                }
            }
        }
    },
    force: {
        itemStyle: {
            normal: {
                linkStyle: {
                    strokeColor: '#408829'
                }
            }
        }
    },
    chord: {
        padding: 4,
        itemStyle: {
            normal: {
                lineStyle: {
                    width: 1,
                    color: 'rgba(128, 128, 128, 0.5)'
                },
                chordStyle: {
                    lineStyle: {
                        width: 1,
                        color: 'rgba(128, 128, 128, 0.5)'
                    }
                }
            },
            emphasis: {
                lineStyle: {
                    width: 1,
                    color: 'rgba(128, 128, 128, 0.5)'
                },
                chordStyle: {
                    lineStyle: {
                        width: 1,
                        color: 'rgba(128, 128, 128, 0.5)'
                    }
                }
            }
        }
    },
    gauge: {
        startAngle: 225,
        endAngle: -45,
        axisLine: {
            show: true,
            lineStyle: {
                color: [
                    [0.2, '#86b379'],
                    [0.8, '#68a54a'],
                    [1, '#408829']
                ],
                width: 8
            }
        },
        axisTick: {
            splitNumber: 10,
            length: 12,
            lineStyle: {
                color: 'auto'
            }
        },
        axisLabel: {
            textStyle: {
                color: 'auto'
            }
        },
        splitLine: {
            length: 18,
            lineStyle: {
                color: 'auto'
            }
        },
        pointer: {
            length: '90%',
            color: 'auto'
        },
        title: {
            textStyle: {
                color: '#333'
            }
        },
        detail: {
            textStyle: {
                color: 'auto'
            }
        }
    },
    textStyle: {
        fontFamily: 'Arial, Verdana, sans-serif'
    }
};


function parseChartData(data){
    console.log("parseChartData start !!");
    console.log(data);

    let statistic = [];
    data.forEach( (prop) =>{
        //console.log(prop);

        let isexisted = false;

        if( statistic.length > 0 ){
            statistic.some( (itr, index)=>{
                //console.log(itr.name);
                if( itr.name == prop.value ){
                    isexisted = true;
                    itr.value += 1;
                    //console.log(itr.name + " : " + itr.value );
                    return true;
                }
            });
        }

        if (false == isexisted){
            statistic.push( { "name":prop.value, "value": 1 } )
        }
    });

    return statistic
}

function setChartDonutData(elmid, input){
    if ($('#'+ elmid ).length) {

        let elem = document.getElementById(elmid);
        elem.style.cssText = "height:450px;";

        let legends = [];
        let count = 0;
        input.some( (itr, index) => {
           legends.push(itr.name);
           count += 1;
           //[MEMO] if there is too many legends, it can't draw appropriately.
           if( count > 8){
               return true;
           }
        });

        let echartDonut = echarts.init(document.getElementById(elmid), theme);

        echartDonut.setOption({
            tooltip: {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%)"
            },
            calculable: true,
            legend: {
                x: 'center',
                y: 'bottom',
                data: legends
            },
            toolbox: {
                show: true,
                feature: {
                    magicType: {
                        show: true,
                        type: ['pie', 'funnel'],
                        option: {
                            funnel: {
                                x: '25%',
                                width: '50%',
                                funnelAlign: 'center',
                                max: 1548
                            }
                        }
                    },
                    restore: {
                        show: true,
                        title: "Restore"
                    },
                    saveAsImage: {
                        show: true,
                        title: "Save Image"
                    }
                }
            },
            series: [{
                name: 'Access to the resource',
                type: 'pie',
                radius: ['35%', '55%'],
                itemStyle: {
                    normal: {
                        label: {
                            show: true
                        },
                        labelLine: {
                            show: true
                        }
                    },
                    emphasis: {
                        label: {
                            show: true,
                            position: 'center',
                            textStyle: {
                                fontSize: '14',
                                fontWeight: 'normal'
                            }
                        }
                    }
                },
                data: input
            }]
        });

    }
}

function setScatterCharts(elmid, input){
    if ($('#'+ elmid ).length) {

        let elem = document.getElementById(elmid);
        elem.style.cssText = "height:450px;";

        let echartScatter = echarts.init(document.getElementById(elmid), theme);

        echartScatter.setOption({
            tooltip: {
                trigger: 'axis',
                showDelay: 0,
                axisPointer: {
                    type: 'cross',
                    lineStyle: {
                        type: 'dashed',
                        width: 1
                    }
                }
            },
            toolbox: {
                show: true,
                feature: {
                    saveAsImage: {
                        show: true,
                        title: "Save Image"
                    }
                }
            },
            xAxis: [{
                type: 'value',
                scale: true,
                name:'',
                nameLocation: 'center',
                nameGap : 30,
                axisLabel: {
                    formatter: '{value}',
                    rotate: 90,
                }
            }],
            yAxis: [{
                type: 'value',
                scale: true,
                name:'',
                nameLocation: 'center',
                nameGap : 30,
                axisLabel: {
                    formatter: '{value}',
                    rotate: 0,
                }
            }],
            series: [{
                name: 'data',
                type: 'scatter',
                tooltip: {
                    trigger: 'item',
                    formatter: function (params) {
                        if (params.value.length > 1) {
                            return params.seriesName + ' :<br/>' + params.value[0] + 'mm' + params.value[1] + 'm2 ';
                        } else {
                            return params.seriesName + ' :<br/>' + params.name + ' : ' + params.value + 'm2 ';
                        }
                    }
                },
                symbolSize: 20,
                data: input,
                markPoint: {
                    data: [{
                        type: 'max',
                        name: 'Max'
                    }, {
                        type: 'min',
                        name: 'Min'
                    }]
                },
                markLine: {
                    data: [{
                        type: 'average',
                        name: 'Mean'
                    }]
                }
            }]
        });
    }
}