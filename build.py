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

    # Grid of product cards. Each card is a button that opens that product's
    # detail panel (handled by the store's own script — no page reload).
    cards = ''
    for item in items:
        cards += f'''
            <button class="store-item" type="button" data-product="{item['id']}">
                <div class="store-item-img"><img src="{item['image']}" alt="{item['name']}"></div>
                <div class="item-name">{item['name']}</div>
                <div class="item-price">{item['price']}</div>
            </button>
        '''

    # One detail panel per product: gallery (main image + thumbnails),
    # title, price, description and buy link.
    panels = ''
    for item in items:
        images = item.get('images') or [item['image']]
        thumbs = ''
        for i, src in enumerate(images):
            active = ' active' if i == 0 else ''
            thumbs += f'<button type="button" class="product-thumb{active}" data-src="{src}"><img src="{src}" alt=""></button>'

        details = ''
        if item.get('details'):
            lis = ''.join(f'<li>{d}</li>' for d in item['details'])
            details = f'<ul class="product-details">{lis}</ul>'

        panels += f'''
            <div class="store-product" id="product-{item['id']}" hidden>
                <button class="store-back" type="button">&larr; Back to store</button>
                <div class="product-layout">
                    <div class="product-gallery">
                        <div class="product-main"><img src="{images[0]}" alt="{item['name']}"></div>
                        <div class="product-thumbs">{thumbs}</div>
                    </div>
                    <div class="product-info">
                        <h2>{item['name']}</h2>
                        <div class="product-price">{item['price']}</div>
                        <p class="product-desc">{item['description']}</p>
                        {details}
                        <a class="product-buy" href="{item['link']}" target="_blank" rel="noopener">Add to cart</a>
                    </div>
                </div>
            </div>
        '''

    return cards, panels


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

    cssFiles = ['nav.css', 'music.css', 'store.css', 'sign-up.css', 'side-quests.css', 'work.css']

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
            store_cards, store_panels = get_store_html()
            contents = contents.replace('{{STORE_ITEMS}}', store_cards).replace('{{STORE_PRODUCTS}}', store_panels)
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