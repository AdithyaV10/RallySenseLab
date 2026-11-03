import {mkdir, readFile, writeFile, copyFile, readdir} from "node:fs/promises";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
import path from "node:path";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const web=path.join(root,"apps/web");
const lock=JSON.parse(await readFile(path.join(root,"data/assets.lock.json"),"utf8"));
const vendor=path.join(web,"public/vendor");
await mkdir(path.join(vendor,"wasm"),{recursive:true});
const pkg=path.join(web,"node_modules/@mediapipe/tasks-vision");
const metadata=JSON.parse(await readFile(path.join(pkg,"package.json"),"utf8"));
if(metadata.version!==lock.runtime_version) throw new Error("MediaPipe version differs from asset lock");
for(const name of await readdir(path.join(pkg,"wasm"))) await copyFile(path.join(pkg,"wasm",name),path.join(vendor,"wasm",name));
await copyFile(path.join(pkg,"vision_bundle.js"),path.join(vendor,"vision_bundle.js"));
for(const asset of lock.assets){
  const target=path.join(vendor,asset.filename);
  let bytes;
  try{bytes=await readFile(target);}catch{const response=await fetch(asset.url);if(!response.ok)throw new Error(`Asset request failed ${response.status}`);bytes=Buffer.from(await response.arrayBuffer());}
  const sha=createHash("sha256").update(bytes).digest("hex");
  if(asset.sha256 && asset.sha256!==sha)throw new Error(`Checksum mismatch: ${asset.filename}`);
  await writeFile(target,bytes);
  console.log(`${asset.filename}: ${sha} (${bytes.length} bytes)`);
  if(asset.filename.endsWith(".task")) await writeFile(path.join(web,"public/model-info.json"),JSON.stringify({runtime_version:metadata.version,model_sha256:sha,model_url:asset.url},null,2));
}
