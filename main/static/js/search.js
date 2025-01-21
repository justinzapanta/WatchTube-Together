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