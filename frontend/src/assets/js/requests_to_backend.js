export async function PostRequest(url, content) {
    const Options = {
        header: "application/json",
        body: content,
        method: "post"
    }
    const resquest = await fetch(url, Options)
    if (!resquest.ok) {
        console.log(`Falied Request ... \n Error: ${resquest.statusText}`);


    }
    else {
        const returns_request = await resquest.json()
        return returns_request;

    }

}
export async function GetRequest(url) {

    const resquest = await fetch(url)
    if (!resquest.ok) {
        console.log(`Falied Request ... \n Error: ${resquest.statusText}`);


    }
    else {
        const returns_request = await resquest.json()
        return returns_request;

    }

}
export async function PuteRequest(url,content) {
    const Options = {
        headers: "application/json",
        body: content,
        methods: "pute"
    }
    const resquest = await fetch(url, Options)
    if (!resquest.ok) {
        console.log(`Falied Request ... \n Error: ${resquest.statusText}`);


    }
    else {
        const returns_request = await resquest.json()
        return returns_request;

    }

}
export async function DeleteRequest(url,) {
    const Options = {
        headers: "application/json",
        methods: "delete"
    }
    const resquest = await fetch(url, Options)
    if (!resquest.ok) {
        console.log(`Falied Request ... \n Error: ${resquest.statusText}`);


    }
    else {
        const returns_request = await resquest.json()
        return returns_request;

    }

}