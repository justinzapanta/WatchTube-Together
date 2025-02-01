const websocket = new WebSocket(`wss://${window.location.host}/ws/global/`)

websocket.onopen = () => {
    const meta = document.querySelector('meta[name="is_online"]');
    const content = meta.getAttribute('content')
    
    if (content !== ''){
        websocket.send(JSON.stringify({
            status : 'Online',
            username : content
        }))
    }
}


function change_status_color(username, status, color, remove_color){
    const status_text = document.getElementById(`${username}-status`)
    const status_icon = document.getElementById(`${username}-icon`)


    status_text.textContent = status
    status_text.classList.remove(`text-${remove_color}`)
    status_icon.classList.remove(`bg-${remove_color}`)
    status_text.classList.add(`text-${color}`)
    status_icon.classList.add(`bg-${color}`)
}


websocket.onmessage = (event) => {
    const meta = document.querySelector('meta[name="is_online"]');
    const content = meta.getAttribute('content')
    const data = JSON.parse(event.data)

    if (data['action'] === 'status'){
        let remove_color
        let color

        if (data['status'] === 'Online'){
            try{
                change_status_color(data['username'], 'Online', 'emerald-500', 'red-500')
                status_text.textContent = 'Online'
            }catch{}
        }else if(data['status'] === 'Offline'){
            try{
                change_status_color(data['username'], 'Offline', 'red-500',  'emerald-500')
                status_text.textContent = 'Online'
            }catch{}
        }
    }else if(data['action'] === 'invitation'){
        console.log(data['link'])
        try{
            if (data['username'] === content){
                display_modal('invitation_modal', 'display')

                const invitation_link = document.getElementById('invitation_link')
                invitation_link.href = data['link']
            }
        }catch{}
    }
}


