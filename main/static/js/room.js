const getCSRFToken = () => {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

const id = document.getElementById('room').getAttribute('video_id')

function onYouTubePlayerAPIReady() {
    player = new YT.Player('player', {
        width: '100%',
        videoId: id,
        playerVars: {
            'rel': 0,            // Recommendations from the same channel
            'modestbranding': 1, // Less prominent YouTube logo
            'showinfo': 0,       // Deprecated but sometimes still effective
            'controls': 1,       // Show controls
            'disablekb': 1       // Disable keyboard controls
            },
        events : {
            onReady : on_player_ready,
            onStateChange : detect_changes
        }
    });
}

onYouTubePlayerAPIReady()

function on_player_ready(event){
    console.log('ready')
}

current_time = 0
function detect_changes(event){
    if (event.data === YT.PlayerState.PLAYING){
        console.log(player.getCurrentTime())
    }else if (event.data == YT.PlayerState.PAUSED){
        current_time = player.getCurrentTime()
        console.log(current_time)
    }else if (event.data == YT.PlayerState.CUED){
        console.log('ewan')
    }
}

const button_icon = document.getElementById('button_icon')

function play_video(){
    if (button_icon.classList.contains('fa-play')){
        button_icon.classList.replace('fa-play', 'fa-pause')
        player.playVideo()
    }else{
        button_icon.classList.replace('fa-pause', 'fa-play')
        player.pauseVideo()
    }
}



function display_modal(id, display=false){
    const modal = document.getElementById(id)

    if(display){
        if (modal.classList.contains('hidden')){
            modal.classList.remove('hidden')
        }
    }else{ 
        modal.classList.add('hidden')
    }
}


async function search(input_id){
    display_modal('search_modal', 'true')
    const input = document.getElementById(input_id)

    if (input.value !== ''){
        const response = await fetch(`/api/videos?search=${input.value}`, {
            method : 'GET',
            headers : {'Content-Type' : 'application/json'}
        })

        const response_json = await response.json()
        const result_div = document.getElementById('result_div') 
        
        response_json.result.forEach(result => {
            const new_div = document.createElement('div')
            new_div.classList.add('w-full', 'flex', 'flex-col', 'hover:cursor-pointer')
            new_div.onclick = () => selected_video(result.id)

            new_div.innerHTML = `
                <div class="w-full h-44 bg-black mt-6">
                    <img src="${result.image}" class="w-full h-44 object-cover object-center" alt="">
                </div>

                <div class="px-2 mt-0.5">
                    <h1 class="line-clamp-2 text-sm">${result.title}</h1>
                </div>
            `

            result_div.appendChild(new_div)
        })
        input.value = ''
    }
}


async function selected_video(id){
    const res = await fetch('/api/room', {
        method: 'PUT',
        headers : {'Content-Type' : 'application/json', 'X-CSRFToken': getCSRFToken()},
        body: JSON.stringify({ video_id : id })
    });

    const res_json = await res.json()
    if (res_json.result !== 'error'){
        window.location.href = `/room/${res_json.result.room_code}/${res_json.result.room_video_id}`
    }
}