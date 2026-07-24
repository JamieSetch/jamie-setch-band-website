

function navigateTo(page) {
    const current = document.querySelector('.page:not(.hidden)')
    if (current) {
        current.classList.add('hidden')
    }
    const next = document.querySelector('#' + page)
    next.classList.remove('hidden')

    // reset the Starlings signup card to its form state whenever it's opened
    if (page === 'starling-signup') {
        const card = next.querySelector('.ss-card')
        if (card) {
            const body = card.querySelector('.ss-body')
            const success = card.querySelector('.ss-success')
            const email = card.querySelector('input[type="email"]')
            if (body) body.classList.remove('hidden')
            if (success) success.classList.add('hidden')
            if (email) email.value = ''
        }
    }

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


function openSignup() {
    // the bottom banner behaves differently per page
    const current = document.querySelector('.page:not(.hidden)')
    const page = current ? current.id : ''
    if (page === 'side-quests') {
        // Travel "Join an Adventure" banner → external adventures site
        window.open('https://seehimal.com', '_blank', 'noopener')
        return
    }
    navigateTo(page === 'music' ? 'starling-signup' : 'sign-up')
}

// Wire the custom-styled Starlings popup to MailerLite (same list/form as the
// Side Quests newsletter embed, form 138280975950939531 on account 1190565).
// The request is POSTed into a hidden iframe so it goes cross-origin without
// CORS and without navigating the page — the same POST MailerLite's own form
// makes. The iframe response is cross-origin/unreadable, so success is shown
// optimistically.
function subscribeStarling(form) {
    const input = form.querySelector('input[type="email"]')
    const email = (input.value || '').trim()
    if (!email) return false

    let sink = document.getElementById('ml-sink')
    if (!sink) {
        sink = document.createElement('iframe')
        sink.id = 'ml-sink'
        sink.name = 'ml-sink'
        sink.style.display = 'none'
        document.body.appendChild(sink)
    }

    const post = document.createElement('form')
    post.action = 'https://assets.mailerlite.com/jsonp/1190565/forms/138280975950939531/subscribe'
    post.method = 'post'
    post.target = 'ml-sink'
    post.style.display = 'none'
    post.innerHTML =
        '<input type="email" name="fields[email]">' +
        '<input type="hidden" name="ml-submit" value="1">' +
        '<input type="hidden" name="anticsrf" value="true">'
    post.querySelector('input[type="email"]').value = email
    document.body.appendChild(post)
    post.submit()
    setTimeout(() => post.remove(), 0)

    const card = form.closest('.ss-card')
    card.querySelector('.ss-body').classList.add('hidden')
    card.querySelector('.ss-success').classList.remove('hidden')
    return false
}

window.site = {}
window.site.navigateTo = navigateTo
window.site.openSignup = openSignup
window.site.subscribeStarling = subscribeStarling
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