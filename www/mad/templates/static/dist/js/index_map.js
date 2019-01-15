/**
 * Created by lenovo on 2018/7/21.
 */
$(function() {
	"use strict";
	$.getJSON ("/static/report/server_map.json", function (data) {
	// $.getJSON ("testFiles/server_map.json", function (data) {
        $('#world_map_marker_1').vectorMap(
            {
                map: 'world_mill_en',
                backgroundColor: 'transparent',
                borderColor: '#fff',
                borderOpacity: 0.25,
                borderWidth: 0,
                color: '#e6e6e6',
                regionStyle: {
                    initial: {
                        fill: '#ccc'
                    }
                },

                markerStyle: {
                    initial: {
                        r: 5,
                        'fill': '#f73414',
                        'fill-opacity': 1,
                        'stroke': '#000',
                        'stroke-width': 1,
                        'stroke-opacity': 0.4
                    },
                },

                markers: data,
                hoverOpacity: null,
                normalizeFunction: 'linear',
                zoomOnScroll: true,
                scaleColors: ['#000000', '#000000'],
                selectedColor: '#000000',
                selectedRegions: [],
                enableZoom: false,
                hoverColor: '#fff'
            });
    });
});