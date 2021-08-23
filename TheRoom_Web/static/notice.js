var pages

$.ajax({
        url: "/noticelist/",
        data: {
            "page": $('#num').html(),
        },
        dataType: "json",
        success: function(data) {
            $('.notice_list').html(data.notice)
            add_pagination(1,data.page_len)
        },
        error: function(e) {

        }
    })
// initialize




// var navs = $('.nav_box li a');
// var nav_title = $('.nav_title');

// // origin 클릭했을때
// navs.off('click').on('click', function(e) {
//     $('.tag_box label').removeClass('text-muted');
//     $('input:checked').prop('checked', false);
    
    
//     navs.removeClass('active');
//     this.classList.add('active');
//     navs.removeClass('fw-bold')
//     e.target.classList.add('fw-bold')
//     nav_title.text(this.innerText + ' 공지사항');
//     $.ajax({
//         url: "getpageinfo/",
//         data: {
//             "origin": e.target.text,
//             "search" : $(".search").val(),
//             "num": 1,
//             "tags": ""
//         },
//         dataType: "json",


//         success: function(data) {
//             add_pagination(1,data.posts_len)
//         },
//         error: function(e) {

//         }

//     })
    
// })




// var first_page = $('.page_num')

// //num -> 몇번부터 띄울건지, max_len 유효성 검사용
function add_pagination(num,max_len) {

    var page_html = "<li class='lbtn page-item'><a class='page-link' taonex='-1' aria-disabled='true'>&laquo;</a></li>"
    var pagination = $('.pagination')

        // console.log(data.posts_len)
    for (i = num; i <num+5; i++) {
        if(i > max_len){
            break;
        }
        page_html = page_html + '<li class="page_num page-item"><a href="/category/notice/'+i+'" class="page-link">' + i + '</a></li>'
    }
    page_html = page_html + "<li class='rbtn page-item'><a class='page-link'>&raquo;</a></li>"



    pagination.html(page_html)
    $('.page_num')[parseInt($('#num').html())-1].classList.add('active')
    pages = $('.pagination .page_num')
    
    // 버튼추가
    var lbtn = $('.lbtn')
    var rbtn = $('.rbtn')
    if (num == 1){
        lbtn.addClass('disabled')
    }
    lbtn.on('click', function() {
        if (lbtn.hasClass('disabled')) {
            return;
        } else {
            var active_page = $('.pagination .active');
            var page_all = $('.page_num');
            // console.log(page_all.index(active_page));
            // page_all[page_all.index(active_page) - 1].click()
            add_pagination(num-5,max_len)
        }
    })
    // console.log(num,max_len)
    if (num+5 > max_len){
        
        rbtn.addClass('disabled')
    }

    rbtn.on('click', function() {
        if (rbtn.hasClass('disabled')) {
            return;
        } else {
            var active_page = $('.pagination .active');
            var page_all = $('.page_num');
            // console.log(page_all.index(active_page));
            // page_all[page_all.index(active_page) + 1].click()
            add_pagination(num+5,max_len)
        }
    })
}