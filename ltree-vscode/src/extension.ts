import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec, spawn } from 'child_process';


function splitArguments(argsString: string): string[] {
    const args: string[] = [];
    let current = '';
    let inDoubleQuotes = false;
    let inSingleQuotes = false;

    for (let i = 0; i < argsString.length; i++) {
        const char = argsString[i];

        if (char === '"' && !inSingleQuotes) {
            inDoubleQuotes = !inDoubleQuotes;
        } else if (char === "'" && !inDoubleQuotes) {
            inSingleQuotes = !inSingleQuotes;
        } else if (char === ' ' && !inDoubleQuotes && !inSingleQuotes) {
            if (current.length > 0) {
                args.push(current);
                current = '';
            }
        } else {
            current += char;
        }
    }
    if (current.length > 0) {
        args.push(current);
    }
    return args;
}

export function activate(context: vscode.ExtensionContext) {
	const runLtree = async (uri: vscode.Uri, format: string | undefined) => {
		let selectedPath = uri ? uri.fsPath : vscode.window.activeTextEditor?.document.uri.fsPath;
        
        if (!selectedPath) {
            vscode.window.showErrorMessage("ltree: No file or folder selected.");
            return;
        }

		let targetDir: string;
		try {
            const stats = fs.statSync(selectedPath);
            targetDir = stats.isDirectory() ? selectedPath : path.dirname(selectedPath);
        } catch (err) {
            vscode.window.showErrorMessage(`ltree: Error accessing path.`);
            return;
        }

        const config = vscode.workspace.getConfiguration('ltree');
        const pythonPath = config.get('pythonPath', 'python');

        const theme = config.get<string>('theme', 'emoji');
		const showSize = config.get<boolean>('showSize', false);
		const dirsFirst = config.get<boolean>('dirsFirst', false);

		let finalFormat = format;
		let extraArgs = config.get<string>('args', '');

		if (!format) {
            // 1. format
            const selectedFormat = await vscode.window.showQuickPick(['text', 'rich', 'json', 'markdown', 'block'], {
                placeHolder: 'Select output format'
            });
            if (!selectedFormat) { return; }			// Esc canceled
            finalFormat = selectedFormat;

            // 2. arguments
            const customArgs = await vscode.window.showInputBox({
                prompt: "Enter additional arguments for ltree",
                placeHolder: "--all -L 2 --re-ex 'pattern'",
                value: extraArgs
            });
            if (customArgs === undefined) { return; } 	// Esc canceled
            extraArgs = customArgs;
        }

        if (!finalFormat) {
            return;
        }

        // Extension module settings
        const spawnArgs: string[] = ['-m', 'ltree.cli', targetDir, '-F', finalFormat];

        if (theme !== 'emoji') {
            spawnArgs.push('--theme', theme);
        }
        if (showSize) {
            spawnArgs.push('--size');
        }
        if (dirsFirst) {
            spawnArgs.push('--dirs-first');
        }

        if (extraArgs.trim().length > 0) {
            const parsedArgs = splitArguments(extraArgs);
            spawnArgs.push(...parsedArgs);
        }

        const env = Object.assign ({}, process.env, {
            PYTHONIOENCODING: "utf-8" 
        });

		vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `ltree: Generating ${finalFormat} format tree structure diagram...`,
        }, () => {
            return new Promise((resolve, reject) => {
                const child = spawn(pythonPath, spawnArgs, { cwd: targetDir, env: env });

                let stdout = '';
                let stderr = '';

                child.stdout.on('data', (data) => {
                    stdout += data.toString();
                });

                child.stderr.on('data', (data) => {
                    stderr += data.toString();
                });

                child.on('error', (err) => {
                    vscode.window.showErrorMessage(`ltree Error: Failed to start process. ${err.message}`);
                    reject(err);
                });

                child.on('close', (code) => {
                    if (code !== 0) {
                        console.error('ltree spawn process error code:', code);
                        vscode.window.showErrorMessage(`ltree Error: ${stderr || `Process exited with code ${code}`}`);
                        return reject();
                    }
                    
                    vscode.env.clipboard.writeText(stdout).then(() => {
                        vscode.window.showInformationMessage(`ltree: Copied to clipboard!`);
                        resolve(null);
                    });
                });
            });
        });
	};

    context.subscriptions.push(
		vscode.commands.registerCommand('ltree.copyTree', (u) => runLtree(u, 'text')),
        vscode.commands.registerCommand('ltree.copyTreeJson', (u) => runLtree(u, 'json')),
        vscode.commands.registerCommand('ltree.copyTreeMarkdown', (u) => runLtree(u, 'markdown')),
        vscode.commands.registerCommand('ltree.copyTreeMarkdownBlock', (u) => runLtree(u, 'block')),
        vscode.commands.registerCommand('ltree.copyTreeCustom', (u) => runLtree(u, undefined))
	);
}

export function deactivate() {}
