import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec } from 'child_process';

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

		let finalFormat = format;
		let extraArgs = config.get('args', '');

		if (!format) {
            // 1. format
            const selectedFormat = await vscode.window.showQuickPick(['text', 'json', 'markdown', 'block'], {
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

		// Construct cmd
        const cmd = `${pythonPath} -m ltree.cli "${targetDir}" -F ${finalFormat} ${extraArgs}`;

        const env = Object.assign ({}, process.env, {
            PYTHONIOENCODING: "utf-8" 
        });

		vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `ltree: Generating ${format} format tree structure diagram...`,
        }, () => {
            return new Promise((resolve, reject) => {
                exec(cmd, { cwd: targetDir, env: env }, (error, stdout, stderr) => {
                    if (error) {
						console.error('ltree exec error:', error);
                        vscode.window.showErrorMessage(`ltree Error: ${stderr || error.message}`);
                        return reject();
                    }
					
					// Write the results to the clipboard
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