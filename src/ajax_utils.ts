function parsedCookies(): {[key: string]: string} {
    const kvpairs = document.cookie.split(';');

    let out: {[key: string]: string} = {};

    kvpairs.forEach(s => {
        const ss = s.trim().split('=');
        if (ss.length == 2) {
            out[ss[0]] = ss[1];
        }
    });

    return out;
}

export function safePost(uri: string, payload: object) {
    return fetch(uri, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': parsedCookies()['csrftoken'],
        },
        body: JSON.stringify(payload),
    })
}