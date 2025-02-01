const getCSRFToken = () => {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
};

const id = document.getElementById('room').getAttribute('video_id')
const room_code = document.getElementById('room').getAttribute('room_code')
const owner = document.getElementById('room').getAttribute('owner')
const username = document.getElementById('room').getAttribute('user')
const user_name = document.getElementById('room').getAttribute('user_name')



let player

function onYouTubePlayerAPIReady() {
    try{
        player = new YT.Player('player', {
            width: '100%',
            videoId: id,
            playerVars: {
                'rel': 0,            // Recommendations from the same channel
                'modestbranding': 1, // Less prominent YouTube logo
                'showinfo': 0,       // Deprecated but sometimes still effective
                'controls': 1,       // Show controls
                'disablekb': 1,       // Disable keyboard controls
                },
            events : {
                onReady : on_player_ready,
                onStateChange : detect_changes
            }
        });
    }catch{
        window.location.reload()
    }
}

onYouTubePlayerAPIReady()
let url = `wss://${window.location.host}/ws/room/${room_code}/`
const web_socket = new WebSocket(url)


function on_player_ready(event){
    console.log('error')
    event.target.mute()
    event.target.playVideo()
    event.target.pauseVideo()
}

let current_time = 0
let action_name = ''

function detect_changes(event){
    if (event.data === YT.PlayerState.PLAYING){
        current_time = player.getCurrentTime()
        action_name = 'playing'
        
        action(current_time, action_name)
    }else if (event.data == YT.PlayerState.PAUSED){
        current_time = player.getCurrentTime()
        action_name = 'paused'

        action(current_time, action_name)
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

    web_socket.send(JSON.stringify({
        action : 'change_video',
        video_id : res_json.result.room_video_id
    }))
}


web_socket.onopen = function() {
    console.log("WebSocket connected!");

    web_socket.send(JSON.stringify({
        action : 'new_visitor',
        username : username,
        room_code : room_code
    }))
};


web_socket.onclose = function() {
    console.log("WebSocket disconnected.");
    window.location.reload()
};



function action(time, action){
    if (owner === 'yes'){
        player.unMute()
        web_socket.send(JSON.stringify({
            time : time,
            room_code : room_code,
            action : action
        }))
    }
}



web_socket.onmessage = async (e) => {
    data = JSON.parse(e.data)
    if (owner !== 'yes'){
        if (data['action'] === 'playing'){
            player.seekTo(data['time'], true)
            player.playVideo()
        }else if (data['action'] === 'paused'){
            player.pauseVideo()
        }    
    }

    //leave
    if (data['action'] === 'leave'){
        const response = await fetch('/api/room/visitor', {
            method : "PUT",
            headers : {'Content-Type' : 'application/json', 'X-CSRFToken': getCSRFToken()},
            body : JSON.stringify({
                user : data['data'],
                room_code : room_code
            })
        })
        
        const response_json = await response.json()
        const results = response_json.result
        update_participants(results['result'])

    //new_visitor
    }else if (data['action'] === 'new_visitor'){
        const response = await fetch(`/api/room/visitor?code=${room_code}`, {
            method : "GET",
            headers : {'Content-Type' : 'application/json'},
        })
        const res_json = await response.json()
        const results = res_json.result

        console.log(results)
        update_participants(results['result'])
        console.log('bumalik')
    }

    // message
    else if (data['action'] == 'message'){
        if (data['sender_email'] !== username){
            display_message(data['message'], 'start', data['sender'])
        }
    }

    //change video

    else if (data['action'] === 'change_video'){
        window.location.href = `/room/${room_code}/${data['video_id']}`
    }

    //friend_request
    else if (data['action'] === 'friend_reqeust'){
        if (data['user'] === username && data['sender'] !== username){
            friend_reqInfo(data['sender'], data['user'], data['sender_name']) //user = friend
        }
    }
}



function update_participants(data){
    const participant_container = document.getElementById('participant_container')
    participant_container.innerHTML = ''
    data.forEach(result => {
        console.log(result)
        const new_div = document.createElement('div')
        new_div.classList.add('bg-gray-700', 'rounded-full', 'hover:cursor-pointer', 'p-2', 'flex', 'items-center', 'space-x-2')
        new_div.onclick = () => display_profile('view_visitor_modal', 'display', result['username'])

        new_div.innerHTML = `
            <img src="${result.user_image}" alt="User 1" class="w-8 h-8 rounded-full">
            <span>${result.role}</span>
        `
        participant_container.appendChild(new_div)
    })
}



async function send_message(event){
    event.preventDefault()
    const message = document.getElementById('message_input')
    const message_value = message.value

    web_socket.send(JSON.stringify({
        'action' : 'message',
        'message' : message.value,
        'sender' : user_name,
        'sender_email' : username
    }))

    display_message(message.value, 'end')
    message.value = ''

    const res = await fetch('/api/messages', {
        method : 'POST',
        headers : {
            'Content-Type' : 'application/json',
            'X-CSRFToken' : getCSRFToken()
        },
        body : JSON.stringify({
            chat_code : room_code,
            chat_sender : user_name,
            chat_message : message_value
        })
    })
}



function display_message(message, position, sender='You'){
    const message_container = document.getElementById('message_container')
    const new_message_div = document.createElement('div')
    new_message_div.classList.add('w-full', 'flex', 'flex-col')

    new_message_div.innerHTML = `
        <div class="w-full flex flex-col">
            <div class="px-1 w-full">
                <h1 class="text-${position} text-sm">${sender}</h1>
            </div>
            <div class="w-full flex mt-1 justify-${position}">
                <div class="bg-gray-900  h-auto rounded-xl px-4 py-3 max-w-96">
                    <h1 class="text-${position} text-white break-words">${message}</h1>
                </div>
            </div>
        </div>
    `

    message_container.appendChild(new_message_div)
}



//invite
function display_modal(id, display=false){
    const modal = document.getElementById(id)
    if (display){
        modal.classList.remove('hidden')
    }else{
        modal.classList.add('hidden')
    }
}



async function display_profile(id, display, visitor){
    const response = await fetch(`/api/user-profile?username=${visitor}`, {
        method : 'GET',
        headers : {
            'Content-Type' : 'application/json',
        }
    })

    const response_json = await response.json()
    const result = response_json.result[0]

    console.log(result)
    document.getElementById('user_name').textContent = visitor
    document.getElementById('user_picture').src = result.user_picture
    document.getElementById('add').onclick = () => add_user(visitor, username)
    display_modal(id, display)
}



function add_user(user, sender){
    console.log('friend request sent')
    web_socket.send(JSON.stringify({
        action : 'friend_request',
        user : user,
        sender : sender,
        sender_name : user_name
    }))

    display_modal('view_visitor_modal')
    success_notif('Friend request has been sent')
}



function friend_reqInfo(sender, friend, sender_name){
    document.getElementById('send_text').textContent = `${sender} sent a friend request`
    document.getElementById('accept_button').onclick = () => accept_friendReq(friend, sender, sender_name)
    display_modal('friend_request_modal', 'display')
}


async function accept_friendReq(friend, sender, sender_name){
    display_modal('friend_request_modal')
    const response = await fetch('/api/friends', {
        method : 'POST',
        headers : {
            'Content-Type' : 'application/json',
            'X-CSRFToken' : getCSRFToken()
        },
        body : JSON.stringify({
            friend : friend,
            sender : sender,
            sender_name : sender_name
        })
    })
}


async function display_friends(id, display=false){
    const response = await fetch('/api/friends?filter=Online', {
        method : 'GET',
        headers : {'Content-Type' : 'application/json'}
    })

    const friend_notif = document.getElementById('friend_notif')
    const res_json = await response.json()
    const result = res_json['result']
    const friend_container = document.getElementById('friend_container')
    friend_container.innerHTML = ''

    if (Object.keys(result).length !== 0){
        result.forEach(info => {
            friend_notif.classList.add('hidden')
            const new_card = document.createElement('div')
            new_card.classList.add('flex', 'flex-col', 'w-fit', 'hover:cursor-pointer')
            new_card.onclick = () => send_invitation(info.friend_info.user_auth_credential.username)
            new_card.innerHTML = `
                <div class="w-14 h-14 bg-white rounded-full">
                    <img src="${info.friend_info.user_picture}" alt="" class="w-14 h-14 rounded-full">
                </div>
                <h1 class="mt-1 text-center">${info.friend_name}</h1>
            `
    
            friend_container.appendChild(new_card)
        })
    }else{
        friend_notif.classList.remove('hidden')
    }

    display_modal(id, display)
}


function send_invitation(username){
    display_modal('invite_friend_modal')
    websocket.send(JSON.stringify({
        action : 'invite',
        username : username,
        link : window.location.href
    }))

    success_notif('Invitation sent successfully')
}


function success_notif(text){
    const notif = document.getElementById('success_notif')
    const notif_modal = document.getElementById('notif_modal')

    notif.textContent = text
    notif_modal.classList.remove('hidden')
    setTimeout(() => {
        notif_modal.classList.add('hidden')
      }, 2000); 
}