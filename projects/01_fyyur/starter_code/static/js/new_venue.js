newVenue = document.getElementsById('venue-form').onsubmit = function (e) {
    e.preventDefault();

    fetch('/venues/create', {
        method: 'POST',
        body: JSON.stringify({
            'name': document.getElementById('name'),
            'city': document.getElementById('city'),
            'state': document.getElementById('state'),
            'address': document.getElementById('address'),
            'phone': document.getElementById('phone'),
            'genres': document.getElementById('genres'),
            'website': document.getElementById('website'),
            'facebook_link': document.getElementById('facebook_link'),
            'image_link': document.getElementById('image_link'),
            'website_link': document.getElementById('website_link'),
            'seeking_talent': document.getElementById('seeking_talent'),
            'seeking_description': document.getElementById('seeking_description'),
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}