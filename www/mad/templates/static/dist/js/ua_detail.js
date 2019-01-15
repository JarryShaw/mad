/**
 * Created by lenovo on 2018/7/20.
 */
var count = 0;
$("#results-display").ready(function() {
    // $.getJSON ("testFiles/UA.json", function (data) {
    //     console.log(data);
    $.getJSON ("/report/UA.json", function (data) {
        count = data.length;
        // $.each(data, function (i, item) {
        //     $.getJSON(item, function (data) {
        $.each(data, function (i, item) {
            var info = item.info;
            var Table = "<div class=\"row\"><div class=\"col-md-12\"><h5 class='text-center'>User Agent信息</h5></div></div>"
            Table = Table + "<hr><div class=\"row\"><div class=\"col-md-6\"><h6 class=\"text-center\">类型</h6><p class=\"text-center\">" + info.type + "</p></div><div class=\"col-md-6\"><h6 class=\"text-center\">设备</h6><p class=\"text-center\">" + info.device + "</p></div></div>" +
                "<div class=\"row\"><div class=\"col-md-6\"><h6 class=\"text-center\">操作系统</h6><p class=\"text-center\">" + info.os + "</p></div><div class=\"col-md-6\"><h6 class=\"text-center\">软件</h6><p class=\"text-center\">" + info.browser + "</p></div></div>" +
                "<div class=\"row\"><div class=\"col-md-12\"><h6 class=\"text-center\">恶意服务器</h6><p class=\"text-center\">" + item.dst + "</p></div></div>";
            Table = Table + "<div class=\"row\"><div class=\"col-md-12\"><h5 class='text-center'>通信详细信息</h5></div></div>"
            var connections = '';
            for(let j=0;j<item.connections.length;j++){
                connections = connections + "<hr>";
                connections = connections + "<div class=\"row\"><div class=\"col-md-12\"><h6 class=\"text-center\">本地主机</h6><p class=\"text-center\">" + item.connections[j].src + "</p></div></div>";
                connections = connections + "<div class=\"row\"><div class=\"col-md-6\"><h6 class=\"text-center\">首次活动时间</h6><p class=\"text-center\">" + item.connections[j].stime + "</p></div><div class=\"col-md-6\"><h6 class=\"text-center\">最后活动时间</h6><p class=\"text-center\">" + item.connections[j].etime + "</p></div></div>";
                var connection = item.connections[j].connection;
                for(let k=0;k<connection.length;k++){
                    connections = connections + "<div class=\"row\"><div class=\"col-md-6\"><h6 class=\"text-center\">连接时间</h6><p class=\"text-center\">" + connection[k].time + "</p></div>";
                    if(connection[k].detected_by_cnn){
                        connections = connections + "<div class=\"col-md-6\"><h6 class=\"text-center\">检测手段</h6><p class=\"text-center\"><span class=\"label label-danger\">CNN</span></p></div>";
                    }else{
                        connections = connections + "<div class=\"col-md-6\"><h6 class=\"text-center\">检测手段</h6><p class=\"text-center\"><span class=\"label label-info\">指纹</span></p></div></div>";
                    }
                    connections = connections + "<div class=\"row\"><div class=\"col-md-12\"><h6 class=\"text-center\">连接地址</h6><p class=\"text-center\">" + connection[k].url + "</p></div></div>";
                }
            }
            Table = Table + connections;
            Table = "<p data-toggle=\"modal\" data-target=\".modal" + count.toString() + "\">详细信息</p>" +
                "<div class=\"modal fade modal" + count.toString() + "\" tabindex=\"-1\" role=\"dialog\" aria-labelledby=\"gridSystemModalLabel\" aria-hidden=\"true\" style=\"display: none;\">" +
                "<div class=\"modal-dialog modal-lg\">" +
                "<div class=\"modal-content\">" +
                "<div class=\"modal-header\">" +
                "<button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-hidden=\"true\">×</button>" +
                "<h5 class=\"modal-title\" id=\"myLargeModalLabel\">详细信息</h5>" +
                "</div><div class=\"modal-body\">" +
                Table + "</div><div class=\"modal-footer\">" +
                "<button type=\"button\" class=\"btn btn-danger text-left\" data-dismiss=\"modal\">Close</button>" +
                "</div></div></div></div>";
            // var type;
            // if(item.type===1){
            //     type = "<span class=\"label label-danger\">恶意</span>";
            // }else{
            //     type = "<span class=\"label label-success\">良性</span>";
            // }
            Table = "<tr><td>" + item.name +
                // "</td><td>" + type +
                "</td><td>" + item.stime +
                "</td><td>" + item.etime +
                "</td><td>" + Table + "</td></tr>";
            $("#results-display").append(Table);
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
// window.onload = function() {
//     while(flag===1){}
//     $('#datable_1').DataTable();
// }