function display_modal(id, display=false){
    const modal = document.getElementById(id)

    if (display){
        modal.classList.remove('hidden')
    }else{
        modal.classList.add('hidden')
    }
}


async function create_room(with_videoID=false){
    data = JSON.stringify({create : true})
    if (with_videoID){
        data = JSON.stringify({
            video_id : with_videoID,
            create : true
        })
    }

    const response = await fetch('/api/room', {
        method : 'POST',
        headers : {
            'Content-Type' : 'application/json',
            'X-CSRFToken' : getCSRFToken()
        },
        body : data
    })

    const response_json = await response.json()
    const result = response_json.result
    console.log(result)
    if (response_json.result !== 'error'){
        if (with_videoID){
            window.location.href = `/room/${result.room_code}/${result.room_video_id}`
        }else{
            window.location.href = `/room/${result.room_code}/`
        }
    }
}


async function join_room(){
    const code = document.getElementById('code_input').value
    const response = await fetch(`/api/room?code=${code}`, {
        method : 'GET',
        headers : {
            'Content-Type' : 'application/json',
        },
    })

    const res_json = await response.json()
    const result = res_json.result

    if (res_json.result !== 'Invalid Code'){
        window.location.href = `/room/${result.room_code}/${result.video_id}`
    }else if(res_json.result === 'Invalid Code'){
        document.getElementById('notif').classList.remove('hidden')
    }else{
        
    }
}