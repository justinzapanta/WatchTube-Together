function display_modal(id, display){
    const modal = document.getElementById(id)

    if (display){
        modal.classList.add('hidden')
    }else{
        modal.classList.remove('hidden')
    }
}