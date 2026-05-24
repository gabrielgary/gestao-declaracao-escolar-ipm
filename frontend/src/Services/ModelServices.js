import { GetRequest, PostRequest, PutRequest, DeleteRequest } from './requests';


export async function createRecord(url, data) {
  // Se for um form, transforme em JSON
  let body = new FormData(data)
  //body=data instanceof FormData ? Object.fromEntries(data) : data;
  const response = await PostRequest(url, body);

  return response;
}


export async function listRecords(url) {
  const response = await GetRequest(url);
  console.log(response);
  return response;
}



export async function updateRecord(url, data) {
  const body = data instanceof FormData ? Object.fromEntries(data) : data;
  const response = await PutRequest(url, body);
  console.log(response);
  return response;
}


export async function deleteRecord(url) {
  const response = await DeleteRequest(url);
  console.log(response);
  return response;
}
export function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}