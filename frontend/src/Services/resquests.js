export async function PostRequest(url, content) {
    const Options = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(content)
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
export async function PutRequest(url, content) {
    const Options = {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(content)
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
        header: { "Content-Type": "application/json" }
        ,
        method: "delete"
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