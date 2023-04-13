$().ready(function () {
    $('#chargement').hide();
    // Capture -- bouton sur ecran
    $(document).on("click","#js-capture",function(){
        capture();
    })//fin capture

    //Capture --- bouton clavier
    document.addEventListener("keyup",function(event){
        if(event.code == 'Enter'  || event.code == 'KeyC' || event.code == 'Space'){
            capture()
        }
    })

    //Fonction capturer
    function capture() {
        let d_1 = new Date()
        console.log('capture_'+d_1.getTime())
        let url = "/detect";
        $('#resultat').hide();
        $('#chargement').show();
        $.get(url,{},function(response){
            console.log(response);
            objets = JSON.parse(response)
            types = ''
            result =''
            color_classes = ['success','primary','danger','warning','info','dark']
            color_gradient = ['ff0000','cc6600','ffff00','99cc00','009933']
            for (i = 0; i < objets.length; i++) {
                result += '<tr>'
                color_class = color_classes[Math.floor(Math.random()*color_classes.length)]
                types += '<span class="badge mx-2 bg-'+color_class+'">'+objets[i].nom+'</span>'
                result += '<td>'+objets[i].nom+'</td>'
                result += '<td>'+objets[i].nombre+'</td>'
                result += '<td>'
                for (j=0;j < objets[i].items.length;j++){
                    valeur_percent = parseFloat(objets[i].items[j].confidence*100)
                    width = parseInt(objets[i].items[j].confidence*100)
                    valeur = valeur_percent.toFixed(2)
                    progress_color = '';
                        if(width<=60){
                            progress_color = color_gradient[0]
                        }else if (width<=70 && width >60){
                            progress_color = color_gradient[1]
                        }else if(width<=80 && width >70){
                            progress_color = color_gradient[2]
                        }else if(width<=90 && width >80){
                            progress_color = color_gradient[3]
                        }else if (width>90){
                            progress_color = color_gradient[4]
                        }

                    console.log('progress_color'+progress_color);
                    result += '<div class="row"><div class="row"><div class="col-3"><span class="badge bg-primary">'+(j+1)+' </span></div><div class="col-9"><div class="progress m-1"><div class="progress-bar progress-bar-animated" style="width:'+valeur+'%; background-color:#'+progress_color+'" role="progressbar" aria-valuenow="'+valeur+'" aria-valuemin="0" aria-valuemax="100">'+valeur+'%</div></div></div></div></div>'
                }
                result += '</td></tr>'
            }
            if (objets.length<1){
                result += ' <tr class="text-center"><td colspan="3" >Aucune objets détecté</td></tr>'
            }
            $("#tbl").html(result)
            console.log(objets)

            target = '#captured';
            let d_2 = new Date();
            $('#resultat').show();
            $('#chargement').hide();
            // $(target).attr('src',"{{url_for('static',filename='img/result.jpg')}}?"+d_2.getTime());
            $(target).attr('src',"static/img/result.jpg?"+d_2.getTime());
            console.log("{{url_for('static',filename='img/result.jpg')}}?")

            $("#objets_nb").text(objets.length)
            $('#types').html(types)

            let diff = (d_2.getTime()-d_1.getTime())/1000;
            $("#calcul_duration").text(diff+ ' secondes')
            console.log('response_'+d_2.getTime())
        })
    }
})