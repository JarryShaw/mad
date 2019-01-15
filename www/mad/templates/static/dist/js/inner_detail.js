/**
 * Created by lenovo on 2018/7/18.
 */
var count = 0;
$(function() {
	"use strict";
    // $.getJSON ("testFiles/innerIP.json", function (data) {
    $.getJSON ("/report/innerIP.json", function (data) {
        count = data.length;
        // $.each(data, function (i, item) {
        //     $.getJSON(item, function (data) {
        $.each(data, function (i, item) {
            var UA = item.UA;
            var UATable = "";
            for(let i=0;i<UA.length;i++){
                var info = UA[i].info;
                UATable = UATable + "<div class=\"row\"><div class=\"col-md-12\"><h6 class=\"text-center\">名称</h6><p class=\"text-center\">" + UA[i].name +	"</p></div></div>" +
                    "<div class=\"row\"><div class=\"col-md-6\"><h6 class=\"text-center\">类型</h6><p class=\"text-center\">" + info.type +	"</p></div><div class=\"col-md-6\"><h6 class=\"text-center\">设备</h6><p class=\"text-center\">" + info.device + "</p></div></div>" +
                    "<div class=\"row\"><div class=\"col-md-6\"><h6 class=\"text-center\">操作系统</h6><p class=\"text-center\">" + info.os + "</p></div><div class=\"col-md-6\"><h6 class=\"text-center\">软件</h6><p class=\"text-center\">" + info.browser + "</p></div></div>" +
                    "<div class=\"row\"><div class=\"col-md-6\"><h6 class=\"text-center\">首次活动时间</h6><p class=\"text-center\">" + UA[i].stime + "</p></div><div class=\"col-md-6\"><h6 class=\"text-center\">最后活动时间</h6><p class=\"text-center\">" + UA[i].etime + "</p></div></div>";
                var connections = UA[i].connection;
                for(let j=0;j<connections.length;j++){
                    UATable = UATable + "<hr>"
                    var connection = connections[j];
                    UATable = UATable + "<div class=\"row\"><div class=\"col-md-6\"><h6 class=\"text-center\">连接时间</h6><p class=\"text-center\">" + connection.time + "</p></div>";
                    if(connection.detected_by_cnn){
                        UATable = UATable + "<div class=\"col-md-6\"><h6 class=\"text-center\">检测手段</h6><p class=\"text-center\"><span class=\"label label-danger\">CNN</span></p></div>";
                    }else{
                        UATable = UATable + "<div class=\"col-md-6\"><h6 class=\"text-center\">检测手段</h6><p class=\"text-center\"><span class=\"label label-info\">指纹</span></p></div></div>";
                    }
                    UATable = UATable + "<div class=\"row\"><div class=\"col-md-12\"><h6 class=\"text-center\">连接地址</h6><p class=\"text-center\">" + connection.url + "</p></div></div>";
                }
                if(i<UA.length-1){
                    UATable = UATable + "<hr>";
                }
            }
            UATable = "<p data-toggle=\"modal\" data-target=\"." + item.IP.replace(/\./g,"_") + "\">详细信息</p>" +
                "<div class=\"modal fade " + item.IP.replace(/\./g,"_") + "\" tabindex=\"-1\" role=\"dialog\" aria-labelledby=\"gridSystemModalLabel\" aria-hidden=\"true\" style=\"display: none;\">" +
                "<div class=\"modal-dialog modal-lg\">" +
                "<div class=\"modal-content\">" +
                "<div class=\"modal-header\">" +
                "<button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-hidden=\"true\">×</button>" +
                "<h5 class=\"modal-title\" id=\"myLargeModalLabel\">详细信息</h5>" +
                "</div><div class=\"modal-body\">" +
                UATable + "</div><div class=\"modal-footer\">" +
                "<button type=\"button\" class=\"btn btn-danger text-left\" data-dismiss=\"modal\">Close</button>" +
                "</div></div></div></div>";
            UATable = "<tr><td>" + item.IP +
                "</td><td>" + item.malicious +
                "</td><td>" + UATable + "</td></tr>";
            $("#results-display").append(UATable);
            count--;
            A();
        });
        function A() {
            if(count-1<=0){
                $('#datable_1').DataTable();
            }
            else {}
        }
    });
    //     });
    // });
});
// setTimeout(function() {
//   $('#datable_1').DataTable();
// }, 100 * 1000);
// window.onload = function() {$('#datable_1').DataTable();}
// $(document).ready(function() {
//     $('#datable_1').DataTable();
// });
function Click() {
    myChart.dispatchAction({type: 'focusNodeAdjacency',linkIndex: 0});
}