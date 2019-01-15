/**
 * Created by lenovo on 2018/7/18.
 */
$("#results-display").ready(function() {
    // $.getJSON ("testFiles/outerIP.json", function (data) {
    $.getJSON ("/report/outerIP.json", function (data) {
        var count = data.length;
        // $.each(data, function (i, item) {
        //     $.getJSON(item, function (data) {
        $.each(data, function (i, item) {
            var inner = item.inner;
            var Table = "";
            for(var i=0;i<inner.length;i++){
                Table = Table + "<div class=\"row\"><div class=\"col-md-6\"><h6 class=\"text-center\">主机IP地址</h6><p class=\"text-center\">" + inner[i].IP +	"</p></div><div class=\"col-md-6\"><h6 class=\"text-center\">首次活动时间</h6><p class=\"text-center\">" + inner[i].stime + "</p></div></div>" +
                    "<div class=\"row\"><div class=\"col-md-6\"><h6 class=\"text-center\">UA名称</h6><p class=\"text-center\">" + inner[i].UA +	"</p></div><div class=\"col-md-6\"><h6 class=\"text-center\">最后活动时间</h6><p class=\"text-center\">" + inner[i].etime + "</p></div></div>";
                var connections = inner[i].connection;
                for(let j=0;j<connections.length;j++){
                    var connection = connections[j];
                    Table = Table + "<div class=\"row\"><div class=\"col-md-6\"><h6 class=\"text-center\">连接时间</h6><p class=\"text-center\">" + connection.time + "</p></div>";
                    if(connection.detected_by_cnn){
                        Table = Table + "<div class=\"col-md-6\"><h6 class=\"text-center\">检测手段</h6><p class=\"text-center\"><span class=\"label label-danger\">CNN</span></p></div>";
                    }else{
                        Table = Table + "<div class=\"col-md-6\"><h6 class=\"text-center\">检测手段</h6><p class=\"text-center\"><span class=\"label label-info\">指纹</span></p></div></div>";
                    }
                    Table = Table + "<div class=\"row\"><div class=\"col-md-12\"><h6 class=\"text-center\">连接地址</h6><p class=\"text-center\">" + connection.url + "</p></div></div>";
                }
                if(i<inner.length-1){
                    Table = Table + "<hr>";
                }
            }
            Table = "<p data-toggle=\"modal\" data-target=\"." + item.IP.replace(/\./g,"_") + "\">详细信息</p>" +
                "<div class=\"modal fade " + item.IP.replace(/\./g,"_") + "\" tabindex=\"-1\" role=\"dialog\" aria-labelledby=\"gridSystemModalLabel\" aria-hidden=\"true\" style=\"display: none;\">" +
                "<div class=\"modal-dialog modal-lg\">" +
                "<div class=\"modal-content\">" +
                "<div class=\"modal-header\">" +
                "<button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-hidden=\"true\">×</button>" +
                "<h5 class=\"modal-title\" id=\"myLargeModalLabel\">内部通信IP信息</h5>" +
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
            Table = "<tr><td>" + item.IP +
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
// window.onload = function() {$('#datable_1').DataTable();}
// $(document).ready(function() {
//     $('#datable_1').DataTable();
// });