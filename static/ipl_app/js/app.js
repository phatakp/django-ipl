$(document).ready(function () {
    new WOW().init();

    $('.mid').on('click', function () {

        if ($(this).find('.switch-input').prop('checked') == true) {
            $(this).find('.switch-input').prop('checked', false);
            var $text = $(this).find('.switch-label').data('off');
            $(this).closest('.match-row').find('.bet-form').find("input[name='team']").val($text);
        } else {
            $(this).find('.switch-input').prop('checked', true);
            var $text = $(this).find('.switch-label').data('on');
            $(this).closest('.match-row').find('.bet-form').find("input[name='team']").val($text);
        }
    });

    $('.switch-input').each(function () {
        $(this).closest('.mid').find('div').text('Select Team');
        if ($(this).prop('checked') == true) {
            var $text = $(this).parent().find('.switch-label').data('on');
            $(this).closest('.match-row').find('.bet-form').find("input[name='team']").val($text);
        } else {
            var $text = $(this).parent().find('.switch-label').data('off');
            $(this).closest('.match-row').find('.bet-form').find("input[name='team']").val($text);
        }
    });

    $('.navbar-toggler').on('click', function () {
        if ($(this).find('.cross').css('visibility') == 'hidden') {
            $(this).find('.default').css('visibility', 'hidden');
            $(this).find('.cross').css('visibility', 'visible');
        } else {
            $(this).find('.default').css('visibility', 'visible');
            $(this).find('.cross').css('visibility', 'hidden');
        }
    });

    $('.btn-bet').on('click', function () {
        $(this).closest('.match-row').find('.bet-row').toggleClass('show');
        $(this).closest('.btn-row').find('.btn-winner').toggleClass('show');
        $(this).toggleClass('show');
    });

    $('.btn-winner').on('click', function () {
        $(this).closest('.match-row').find('.winner-row').toggleClass('show');
        $(this).closest('.btn-row').find('.btn-bet').toggleClass('show');
        $(this).toggleClass('show');
    });

    $('.check-bet').on('click', function () {
        $('.bets-row').removeClass('show');
        $('.btns-row').addClass('show');
        $(this).closest('.match-list').find('.bets-row').toggleClass('show');
        $(this).closest('.btns-row').toggleClass('show');
    });
});

$(function () {
    $(".fold-table tr.view").on("click", function () {
        $(this).toggleClass("open").next(".fold").toggleClass("open");
    });
});