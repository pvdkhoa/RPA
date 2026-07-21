using REF_RPA.ObjectRepository;
using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using UiPath.CodedWorkflows;

namespace REF_RPA
{
    public class python_workflow : CodedWorkflow
    {
       [Workflow]
        public void Execute(string scriptPath, string mode = "")
        {
            string pythonExe = @"C:\Users\RPA02\AppData\Local\Programs\Python\Python311\python.exe";

            if (string.IsNullOrWhiteSpace(scriptPath))
            {
                throw new Exception("scriptPath empty.");
            }

            if (!File.Exists(pythonExe))
            {
                throw new Exception("Not Found python.exe: " + pythonExe);
            }

            if (!File.Exists(scriptPath))
            {
                throw new Exception("Not Found Python script: " + scriptPath);
            }

            string workingDirectory = Path.GetDirectoryName(scriptPath);
            if (string.IsNullOrWhiteSpace(workingDirectory))
            {
                throw new Exception("Working Directory Error " + scriptPath);
            }

            string logDir = @"C:\UipathScript\log";
            Directory.CreateDirectory(logDir);

            string stdoutPath = Path.Combine(logDir, "uipath_python_stdout.txt");
            string stderrPath = Path.Combine(logDir, "uipath_python_stderr.txt");
            string commandPath = Path.Combine(logDir, "uipath_python_command.txt");

            var psi = new ProcessStartInfo
            {
                FileName = pythonExe,
                Arguments = $"\"{scriptPath}\" \"{mode}\"",
                WorkingDirectory = workingDirectory,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = false
            };

            psi.EnvironmentVariables["PYTHONUTF8"] = "1";
            psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";

            File.WriteAllText(
                commandPath,
                "PythonExe: " + pythonExe + Environment.NewLine +
                "ScriptPath: " + scriptPath + Environment.NewLine +
                "Mode: " + mode + Environment.NewLine +
                "WorkingDirectory: " + workingDirectory + Environment.NewLine +
                "Command: " + pythonExe + " " + psi.Arguments + Environment.NewLine,
                Encoding.UTF8
            );

            using (var process = new Process())
            {
                process.StartInfo = psi;

                process.Start();

                string stdout = process.StandardOutput.ReadToEnd();
                string stderr = process.StandardError.ReadToEnd();

                process.WaitForExit();

                File.WriteAllText(stdoutPath, stdout ?? "", Encoding.UTF8);
                File.WriteAllText(stderrPath, stderr ?? "", Encoding.UTF8);

                if (process.ExitCode != 0)
                {
                    throw new Exception(
                        "Python failed. ExitCode=" + process.ExitCode +
                        Environment.NewLine +
                        "STDOUT log: " + stdoutPath +
                        Environment.NewLine +
                        "STDERR log: " + stderrPath +
                        Environment.NewLine +
                        "COMMAND log: " + commandPath +
                        Environment.NewLine +
                        stderr
                    );
                }
            }
        }
    }
}



