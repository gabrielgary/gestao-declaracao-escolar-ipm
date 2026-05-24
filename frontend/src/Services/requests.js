export async function handleResponse(response) {
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Request failed with status ${response.status}`);
    }
    return response.json();
}

export async function PostRequest(url, content) {
    const isFormData = content instanceof FormData;
    const options = {
        method: "POST",
        headers: isFormData ? {} : { "Content-Type": "application/json" },
        body: isFormData ? content : JSON.stringify(content)
    };

    try {
        const response = await fetch(url, options);
        return await handleResponse(response);
    } catch (error) {
        console.error("PostRequest Error:", error.message);
        throw error;
    }
}

export async function GetRequest(url) {
    try {
        const response = await fetch(url);
        return await handleResponse(response);
    } catch (error) {
        console.error("GetRequest Error:", error.message);
        throw error;
    }
}

export async function PutRequest(url, content) {
    const isFormData = content instanceof FormData;
    const options = {
        method: "PUT",
        headers: isFormData ? {} : { "Content-Type": "application/json" },
        body: isFormData ? content : JSON.stringify(content)
    };

    try {
        const response = await fetch(url, options);
        return await handleResponse(response);
    } catch (error) {
        console.error("PutRequest Error:", error.message);
        throw error;
    }
}

export async function DeleteRequest(url) {
    const options = {
        method: "DELETE",
        headers: { "Content-Type": "application/json" }
    };

    try {
        const response = await fetch(url, options);
        return await handleResponse(response);
    } catch (error) {
        console.error("DeleteRequest Error:", error.message);
        throw error;
    }
}
