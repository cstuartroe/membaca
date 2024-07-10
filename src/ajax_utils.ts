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

export function safePostForm(uri: string, payload: object, addCsrfToken: boolean) {
    const formData = new URLSearchParams();
    if (addCsrfToken) {
        formData.append("csrfmiddlewaretoken", parsedCookies()['csrftoken']);
    }
    for (const [key, value] of Object.entries(payload)) {
        formData.append(key, value);
    }

    return fetch(uri, {
        method: "POST",
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': parsedCookies()['csrftoken'],
        },
        body: formData,
    })
}
