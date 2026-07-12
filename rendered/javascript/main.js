

function navigateTo(page) {
    const current = document.querySelector('.page:not(.hidden)')
    if (current) {
        current.classList.add('hidden')
    }
    const next = document.querySelector('#' + page)
    next.classList.remove('hidden')
    document.querySelector('nav').dataset.size = next.dataset.nav
    closeSideNav()
    history.pushState('hi', "", page);

    let els = document.querySelectorAll('.nav-link.selected')
    for (const el of els) {
        el.classList.remove('selected')
    }

    els = document.querySelectorAll('.nav-link[data-navid="' + page + '"]')
    for (const el of els) {
        el.classList.add('selected')
    }

    sessionStorage.setItem('last-page', sessionStorage.getItem('current-page'))
    sessionStorage.setItem('current-page', page)
}

function toggleSideNav() {
    document.body.classList.toggle('side-nav-open')
}

function closeSideNav() {
    document.body.classList.remove('side-nav-open')
}

function goBack() {
    navigateTo(sessionStorage.getItem('last-page') || 'home')
}

var playingMusic = false
function setPlayIcon(src) {
    document.querySelectorAll('.np-play-mini img, #np-play-big img').forEach((img) => { img.src = src })
}
function playMusic() {
    document.querySelector('.now-playing').classList.remove('hidden')
    document.querySelector('.now-playing audio').play()
    setPlayIcon('/assets/icons/pause.svg')
    playingMusic = true
}

function pauseMusic() {
    document.querySelector('.now-playing audio').pause()
    setPlayIcon('/assets/icons/play.svg')
    AHHHHHH = true
    playingMusic = false
}


function toggleMusic() {
    if (playingMusic) {
        pauseMusic()
    } else {
        playMusic()
    }
}

document.querySelector('.now-playing audio').volume = 0.1


window.site = {}
window.site.navigateTo = navigateTo
window.site.toggleSideNav = toggleSideNav
window.site.goBack = goBack
window.site.pauseMusic = pauseMusic
window.site.playMusic = playMusic
window.site.toggleMusic = toggleMusic


sessionStorage.setItem('current-page', '')
sessionStorage.setItem('last-page', '')


const els = document.querySelectorAll('.nav-link')
for (const el of els) {
    el.addEventListener('click', (e) => {
        e.preventDefault()
        navigateTo(e.target.dataset.navid)
    })
}

window.addEventListener('popstate', (e) => {
    let path = window.location.pathname
    path = path.slice(1, path.length).split('.')[0]
    navigateTo(path)
})


let path = window.location.pathname
path = path.slice(1, path.length).split('.')[0]
if (path != 'index') {
    navigateTo(path || 'home')
}




var AHHHHHH = false
document.addEventListener('click', (e) => {
    if (!AHHHHHH) {
        playMusic()
    }
})



setInterval(() => {
    const els = document.querySelectorAll('.countdown')
    for (let el of els) {
        let seconds = parseInt(parseInt(el.dataset.date) - (Date.now() / 1000))
        if (seconds < 0) {
            el.innerHTML = el.dataset.name
            continue
        }
        let minutes = parseInt(seconds / 60)
        seconds = seconds % 60

        let hours = parseInt(minutes / 60)
        minutes = minutes % 60

        let days = parseInt(hours / 24)
        hours = hours % 24

        el.innerHTML = `${(days + '').padStart(2, '0')}:${(hours + '').padStart(2, '0')}:${(minutes + '').padStart(2, '0')}:${(seconds + '').padStart(2, '0')}`
    }
}, 1000)