function updateButton(btn, is_active) {
    if (is_active) {
        btn.removeClass('btn-default').addClass('is-active')
        btn.html('<i class="fa fa-heart"></i> Liked')
    } else {
        btn.removeClass('is-active').addClass('btn-default')
        btn.html('<i class="fa fa-heart"></i> Like')
    }
  };
  function updateSubButton(btn, is_active) {
    if (is_active) {
        btn.removeClass('btn-default').addClass('is-active')
        btn.html('<i class="fa fa-plus-square"></i> Following')
    } else {
        btn.removeClass('is-active').addClass('btn-default')
        btn.html('<i class="fa fa-plus-square"></i> Follow')
    }
  };
  $(function() {
      $('#like').on('click', function() {
          var this_ = $(this)
          $.ajax({
              'url':$(change_like),
              'type':'GET',
              'data':{
                  'ep_id':this_.attr('data-episode-id'),
              },
              'dataType':'json'
          })
          .done(function(data){
              updateButton(this_, data.liked)
          })
          .fail(function(data){
              $('#info').attr('class', 'alert alert-danger alert-dismissable')
              $('#info').html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' + '登録できませんでした')
          })
      });
  });
  $(function() {
      $('#collection').on('click', function() {
          var this_ = $(this)
          var title = $('#id_add_collection').val()
          var new_title = $('#id_new').val()
          $.ajax({
              'url':'feed/add_collection.html',
              'type':'GET',
              'data':{
                  'ep_id':this_.attr('data-episode-id'),
                  'col_id':title,
                  'new_title':new_title
              },
              'dataType':'json'
          })
          .done(function(data){
            if (data.is_success) {
              $('#info').attr('class', 'alert alert-success alert-dismissable')
              $('#info').html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' + 'コレクションに追加しました')
              $('#addCollectionModal').modal('hide')
            } else {
              // 選択値不正の場合
              $('.modal-error').html('<p>' + '*どちらか一方のコレクションを選択してください' + '</p>')
              $('.modal-error').attr('class', 'text-danger')
            }
          })
          .fail(function(data){
              $('#info').attr('class', 'alert alert-danger alert-dismissable')
              $('#info').html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' + '登録できませんでした')
              $('#addCollectionModal').modal('hide')
          })
      });
  });
  $(function() {
      $('#subscription').on('click', function() {
          var this_ = $(this)
          $.ajax({
              'url':'feed/change_subscription.html',
              'type':'GET',
              'data':{
                  'ch_id':this_.attr('data-channel-id'),
              },
              'dataType':'json'
          })
          .done(function(data){
              updateSubButton(this_, data.subscription)
          })
          .fail(function(data){
              $('#error').attr('class', 'alert alert-danger alert-dismissable')
              $('#error').html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' + '登録できませんでした')
          })
      });
  });
  /**
  *  RECOMMENDED CONFIGURATION VARIABLES: EDIT AND UNCOMMENT THE SECTION BELOW TO INSERT DYNAMIC VALUES FROM YOUR PLATFORM OR CMS.
  *  LEARN WHY DEFINING THESE VARIABLES IS IMPORTANT: https://disqus.com/admin/universalcode/#configuration-variables*/
  /*
  var disqus_config = function () {
  this.page.url = PAGE_URL;  // Replace PAGE_URL with your page's canonical URL variable
  this.page.identifier = PAGE_IDENTIFIER; // Replace PAGE_IDENTIFIER with your page's unique identifier variable
  };
  */
  (function() { // DON'T EDIT BELOW THIS LINE
  var d = document, s = d.createElement('script');
  s.src = 'https://loguesnap.disqus.com/embed.js';
  s.setAttribute('data-timestamp', +new Date());
  (d.head || d.body).appendChild(s);
  })();