import { access, opendir } from 'node:fs/promises';

import * as esbuild from "esbuild"
import { sassPlugin } from 'esbuild-sass-plugin'

const STATIC_SRC = "static_src"
const STATIC_DEST = "static"

let dirsToBuild = ["config", "upkeep/ui"]

for (const dirToBuild of dirsToBuild) {
  try {
    await access(dirToBuild + "/" + STATIC_SRC)
  } catch (err) {
    continue
  }

  let options = {
    entryPoints: [dirToBuild + "/" + STATIC_SRC + "/**/main.*"],
    outdir: dirToBuild + "/" + STATIC_DEST,
    outbase: dirToBuild + "/" + STATIC_SRC,
    bundle: true,
    minify: true,
    plugins: [sassPlugin({ quietDeps: true })],
    logLevel: 'info',
  }

  try {
    if (process.argv.includes("--watch")) {
      let ctx = await esbuild.context(options)
      await ctx.watch()
    } else {
      let result = await esbuild.build(options)
      console.log(result)
    }
  } catch (err) {
    console.error(err)
  }
}
