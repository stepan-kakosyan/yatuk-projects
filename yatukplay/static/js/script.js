function getLanguage() {
  var hr = location.href.split(location.host)[1].split("/")[1]
  if (hr == "hy" || hr == "ru"){
      return  hr 
  }else{
      return "en"
  }
}
function dynamicSort(property) {
  var sortOrder = 1;
  if(property[0] === "-") {
      sortOrder = -1;
      property = property.substr(1);
  }
  return function (a,b) {
      /* next line works with strings and numbers, 
       * and you may want to customize it to your needs
       */
      var result = (a[property] < b[property]) ? -1 : (a[property] > b[property]) ? 1 : 0;
      return result * sortOrder;
  }
}

var repeat = localStorage.getItem("repeat")
if (repeat === null) {
  window.localStorage.setItem('repeat', 0);
}else if(parseInt(repeat) == 1){
  $('.repeat_icon').addClass('checked');
}
window.localStorage.removeItem('current_album');

$(function () {
  var bgArtwork = $("#bg-artwork"),
      bgArtworkUrl,
      trackName = $("#track-name"),
      albumArt = $("#album-art"),
      seekBar = $("#seek-bar"),
      trackTime = $("#track-time"),
      playPauseButton = $("#play-pause-button"),
      i = playPauseButton.find("i"),
      tProgress = $("#current-time"),
      tTime = $("#track-length"),
      curMinutes,
      curSeconds,
      durMinutes,
      durSeconds,
      playProgress,
      bTime,
      nTime = 0,
      buffInterval = null,
      tFlag = false,
      songs = audios_json
      playPreviousTrackButton = $("#play-previous"),
      currIndex = -1;

  function playPause() {
    setTimeout(function () {
      if (audio.paused) {
        albumArt.addClass("active");
        checkBuffering();
        i.attr("class", "fa fa-pause");
        audio.play();
      } else {
        albumArt.removeClass("active");
        clearInterval(buffInterval);
        albumArt.removeClass("buffering");
        i.attr("class", "fa fa-play");
        audio.pause();
      }
    }, 300);
  }

  var currentSong;
  function updateCurrTime() {
    nTime = new Date();
    nTime = nTime.getTime();

    if (!tFlag) {
      tFlag = true;
      trackTime.addClass("active");
    }

    curMinutes = Math.floor(audio.currentTime / 60);
    curSeconds = Math.floor(audio.currentTime - curMinutes * 60);

    durMinutes = Math.floor(audio.duration / 60);
    durSeconds = Math.floor(audio.duration - durMinutes * 60);

    playProgress = (audio.currentTime / audio.duration) * 100;

    if (curMinutes < 10) curMinutes = "0" + curMinutes;
    if (curSeconds < 10) curSeconds = "0" + curSeconds;

    if (durMinutes < 10) durMinutes = "0" + durMinutes;
    if (durSeconds < 10) durSeconds = "0" + durSeconds;

    if (isNaN(curMinutes) || isNaN(curSeconds)) tProgress.text("00:00");
    else tProgress.text(curMinutes + ":" + curSeconds);

    if (isNaN(durMinutes) || isNaN(durSeconds)) tTime.text("00:00");
    else tTime.text(durMinutes + ":" + durSeconds);

    if (
      isNaN(curMinutes) ||
      isNaN(curSeconds) ||
      isNaN(durMinutes) ||
      isNaN(durSeconds)
    )
      trackTime.removeClass("active");
    else trackTime.addClass("active");

    seekBar.width(playProgress + "%");

    if (playProgress == 100) {
      i.attr("class", "fa fa-play");
      seekBar.width(0);
      tProgress.text("00:00");
      albumArt.removeClass("buffering").removeClass("active");
      clearInterval(buffInterval);
    }
  }

  function checkBuffering() {
    clearInterval(buffInterval);
    buffInterval = setInterval(function () {
      if (nTime == 0 || bTime - nTime > 1000) albumArt.addClass("buffering");
      else albumArt.removeClass("buffering");
      bTime = new Date();
      bTime = bTime.getTime();
    }, 100);
  }


  function selectTrack(flag, id) {
    var current_album = localStorage.getItem("current_album")
    if(flag == -2){
    }else{
    if (flag == 0 || flag == 1) ++currIndex;
    else --currIndex;
    }
    var filtered_songs;
    if (current_album != null && current_album != "undefined"){
      filtered_songs = songs.filter(v => v['author']['id'] == parseInt(current_album)).sort(dynamicSort('name_'+getLanguage()))
    }else{
      filtered_songs = songs
    }
    if (currIndex > -1 || flag == -2) {
      if (currIndex == 0){
        playPreviousTrackButton.addClass("disabled")
      }else{
        playPreviousTrackButton.removeClass("disabled")
      }
      if (flag == 1) {
        if (currIndex == filtered_songs.length){
          currIndex = 0
        }
      }
      if (flag == 0) i.attr("class", "fa fa-play");
      else {
        albumArt.removeClass("buffering");
        i.attr("class", "fa fa-pause");
      }
      if (flag == -2){
          currentSong = filtered_songs.filter(v => v.id == id)[0]
          $(".leaderboard__profiles .leaderboard__profile ").each(function() {
            if($(this).attr('data-id') == id){
              $(this).addClass('active');
              $(this).children('.song-buttons').children('.leaderboard__value').removeClass('enabled').addClass('disabled')
            }else{
              $(this).removeClass('active');
              $(this).children('.song-buttons').children('.leaderboard__value').removeClass('disabled').addClass('enabled')
            }
        });
      }else{
        currentSong = filtered_songs[currIndex]
        if (parseInt(current_album) > 0){
        }else{
        $.ajax({url:"/"+getLanguage()+"/author-info/"+currentSong['id']+"/", success: function(result){
          $("#author_part").html(result);
          htmx.process(htmx.find('.list-song-icon'))
        }});
      }
      }
      $(".leaderboard__profiles .leaderboard__profile ").each(function() {
        if($(this).attr('data-id') == currentSong['id']){
          $(this).addClass('active');
          $(this).children('.song-buttons').children('.leaderboard__value').removeClass('enabled').addClass('disabled')
        }else{
          $(this).removeClass('active');
          $(this).children('.song-buttons').children('.leaderboard__value').removeClass('disabled').addClass('enabled')
        }
    });
      seekBar.width(0);
      trackTime.removeClass("active");
      tProgress.text("00:00");
      tTime.text("00:00");
      currAlbum = currentSong['author']['name_'+getLanguage()];
      currTrackName = currentSong['name_'+getLanguage()];
      currArtwork = currentSong['id'];
      currAvatar = currentSong['author']['image'];
      audio.src = currentSong['audio'];
      nTime = 0;
      bTime = new Date();
      bTime = bTime.getTime();
      if (flag != 0) {
        audio.play();
        $("#player-track").addClass("active");
        albumArt.addClass("active");
        clearInterval(buffInterval);
        checkBuffering();
      }
      $("#album-name").text(currAlbum);
      trackName.text(currTrackName);
      albumArt.find("img.active").removeClass("active");
      $("#" + currArtwork).addClass("active");
      bgArtworkUrl = $("#" + currArtwork).attr("src");
      $('.download_button').children('.download_a').attr('href', '/'+getLanguage()+'/download/'+currentSong['id']+'/')
      $('.download_button').children('.copy-icon').attr('data-url', 'https://play.yatuk.am/'+getLanguage()+'/music/'+currentSong['author']['slug']+"/"+currentSong['slug'])
      bgArtwork.attr('data-id', currentSong['id'])
      bgArtwork.css({ "background-image": "url(" + bgArtworkUrl + ")" });
    } else {
      if (flag == 0 || flag == 1) --currIndex;
      else ++currIndex;
    }
  }

  function initPlayer(){
    audio = new Audio();
    selectTrack(0, -1);
    audio.loop = false;
    playPauseButton.on("click", playPause);
    $(audio).on("timeupdate", updateCurrTime);
    playPreviousTrackButton.on("click", function () {
      selectTrack(-1, -1);
    });
    $("#play-next").on("click", function () {
      selectTrack(1, -1);
    });
    $("body").delegate(".leaderboard__value.enabled", "click",function(){
      selectTrack(-2, $(this).attr('data-id'));
    });
    $("body").delegate(".play_album_icon", "click",function(){
      if ($(this).parent('.play_album').hasClass('checked')){
        $(this).parent('.play_album').removeClass("checked");
        window.localStorage.removeItem('current_album');
      }else{
        $(this).parent('.play_album').addClass('checked');
        window.localStorage.setItem('current_album', $(this).attr('data-id'));
      }
      currIndex = -1
      selectTrack(1, -1);
    });
    audio.addEventListener('ended',function(){
      if (parseInt(repeat) == 1){
        albumArt.addClass('active')
        audio.play();
      }else{
          selectTrack(1, -1);
      }
    });
  }
  initPlayer();
});

$(".option").click(function(){
  $(".option").removeClass("active");
  $(this).addClass("active");
});

function copy(){
  var copyText = $('.download_button .copy-icon');
  copyText.select();
  navigator.clipboard.writeText(copyText.attr('data-url'));
  $(".info-text").show().delay(3000).fadeOut();
}
$('.repeat_icon').click(function(){
  if ($(this).hasClass('checked')){
    $(this).removeClass("checked");
    window.localStorage.setItem('repeat', 0);
  }else{
    $(this).addClass('checked');
    window.localStorage.setItem('repeat', 1);
  }
})

