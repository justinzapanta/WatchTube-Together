function display_modal(id, display=false){
    const modal = document.getElementById(id)

    if (display){
        modal.classList.remove('hidden')
    }else{
        modal.classList.add('hidden')
    }
}


async function create_room(){
    const response = await fetch('/api/room', {
        method : 'POST',
        headers : {
            'Content-Type' : 'application/json',
            'X-CSRFToken' : getCSRFToken()
        },
        body : JSON.stringify({
            'create' : true
        })
    })

    const response_json = await response.json()

    if (response_json.result !== 'error'){
        window.location.href = `/room/${response_json.result}`
    }else{
        pass
    }
}