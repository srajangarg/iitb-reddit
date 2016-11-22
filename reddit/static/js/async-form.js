$(document).on('submit', '#login-form', function(){
    $.ajax({ 
        type: $(this).attr('method'), 
        url: this.action, 
        data: $(this).serialize(),
        context: this,
        success: function(data, status) {
            if(data.success){
                location.reload();
            }
            else{
                alert(data.Error);
            }
        }
    });
    return false;
});

$(document).on('submit', '#signup-form', function(){
    $.ajax({ 
        type: $(this).attr('method'), 
        url: this.action, 
        data: $(this).serialize(),
        context: this,
        success: function(data, status) {
            if(data.success){
                console.log("signed UP")
                location.reload();
            }
            else{
                alert(data.Error);
            }
        }
    });
    return false;
});