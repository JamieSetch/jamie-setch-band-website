import json
import datetime


def get_music_html():
    f = open('items/songs.json')
    songs = json.load(f)
    f.close()

    result = ''
    for song in songs:
        date = ''
        if 'releases' in song.keys():
            date = str(datetime.datetime.strptime(song['releases'], '%d/%m/%Y').timestamp())

        result +=  f'''
            <a data-name="{song['name']}" style='background:{song['background']}; color: {song['text-colour']}' href='{song['link']}' data-date='{date}' class='{'countdown' if date != '' else ''}'>
                <span>{song['name']}</span>
            </a>
        '''
    
    return result


def get_store_html():
    f = open('items/store.json')
    items = json.load(f)
    f.close()

    result = ''
    for item in items:
        result += f'''
            <a class="store-item" href="{item['link']}">
                <img src="{item['image']}" alt="{item['name']}">
                <div class="item-name">{item['name']}</div>
                <div class="item-price">{item['price']}</div>
            </a>
        '''
    
    return result


def build():
    f = open('pages.json')
    pages = json.load(f)
    f.close()

    f = open('items/now-playing.json')
    nowPlaying = json.load(f)
    f.close()

    f = open('unrendered/template.html')
    template = f.read()
    f.close()

    cssFiles = ['nav.css', 'music.css', 'store.css', 'sign-up.css', 'side-quests.css']

    css = ''
    for file in cssFiles:
        f = open(f'unrendered/css/{file}')
        css += f.read()
        f.close()

    template = template.replace('{{MAIN_CSS}}', f'<style>{css}</style>').replace('{{SONG_NAME}}', nowPlaying['name']).replace('{{SONG_FILE}}', nowPlaying['src'])

    f = open('items/socials.json')
    socials = json.load(f)
    f.close()
    social_html = ''
    for social in socials:
        social_html += f'''
            <a href="{social['link']}">

                <svg width="200" height="200">
                    <defs>
                        <filter id="whiteFilter" color-interpolation-filters="sRGB">
                            <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/>
                        </filter>
                        <filter id="yellowFilter" color-interpolation-filters="sRGB">
                            <feColorMatrix type="matrix" values="0 0 0 0 0.98  0 0 0 0 0.90  0 0 0 0 0.11  0 0 0 1 0"/>
                        </filter>
                    </defs>
                    <image href="{social['icon']}" x="0" y="0" height="200px" width="200px"/>
                </svg>
            </a>
        '''
    template = template.replace('{{SOCIALS}}', social_html)

    pageContents = {}

    for page in pages:
        f = open('unrendered/' + page['id'] + '.html')
        contents = f.read()
        if page['id'] == 'music':
            contents = contents.replace('{{MUSIC_LIST}}', get_music_html())
        if page['id'] == 'store':
            contents = contents.replace('{{STORE_ITEMS}}', get_store_html())
        pageContents[page['id']] = contents
        f.close()

    for page in pages:
        contents = ''
        for key in pageContents.keys():
            content = pageContents[key].replace('{{HIDDEN}}', ' hidden ')
            if key == page['id']:
                content = pageContents[key].replace('{{HIDDEN}}', '')
            showNav = [page['show-nav'] for page in pages if page['id'] == key]
            content = content.replace('{{SHOW_NAV}}', showNav[0])
            contents += content
        
        contents = template.replace('{{MAIN_CONTENT}}', contents)
        contents = contents.replace('{{NAV_SIZE}}', page['show-nav'])

        f = open('rendered/' + page['id'] + '.html', 'w+')
        f.write(contents)
        f.close()

        if page['id'] == 'home':
            f = open('rendered/index.html', 'w+')
            f.write(contents)
            f.close()


build()