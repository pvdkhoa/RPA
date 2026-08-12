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

            // ---- Basic validation ----
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

            // ---- Clean up log files older than the retention period ----
            // Runs every time Execute() is called, so no separate Task Scheduler job is needed.
            // Prevents the log folder from growing indefinitely once each run gets its own
            // timestamped log file (see below).
            CleanupOldLogs(logDir, retentionDays: 7);

            // ---- Build unique, timestamped log file names for this run ----
            // Using a timestamp (instead of a fixed file name) avoids overwriting the log
            // from a previous run. This matters because if Python crashes on run N and the
            // next run (N+1) succeeds, a fixed file name would silently overwrite the only
            // evidence of the failure in run N before anyone gets a chance to inspect it.
            string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss_fff");
            string stdoutPath = Path.Combine(logDir, $"uipath_python_stdout_{timestamp}.txt");
            string stderrPath = Path.Combine(logDir, $"uipath_python_stderr_{timestamp}.txt");
            string commandPath = Path.Combine(logDir, $"uipath_python_command_{timestamp}.txt");

            var psi = new ProcessStartInfo
            {
                FileName = pythonExe,
                Arguments = $"\"{scriptPath}\" \"{mode}\"",
                WorkingDirectory = workingDirectory,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,

                // CreateNoWindow = true: do not allocate a console window for the child
                // process. Since stdout/stderr are already redirected and read via
                // process.StandardOutput / StandardError, no visible console is needed.
                // Setting this to false (the original setting) makes Windows allocate a
                // console handle for every single invocation; with a high call volume
                // (14 insurance companies x many transactions per day) this can
                // contribute to exhausting console/desktop-heap resources over time,
                // which is a documented cause of intermittent
                // "ExitCode=-1073741502 (STATUS_DLL_INIT_FAILED)" errors.
                CreateNoWindow = true
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

        /// <summary>
        /// Deletes log files (uipath_python_*.txt) in <paramref name="logDir"/> that are
        /// older than <paramref name="retentionDays"/> days.
        /// Called at the start of every Execute() run so that switching to per-run,
        /// timestamped log files (see Execute above) does not cause the log folder to
        /// grow without bound. Any exception during cleanup is swallowed so that a
        /// housekeeping failure never breaks the main workflow.
        /// </summary>
        /// <param name="logDir">Directory containing the Python invocation log files.</param>
        /// <param name="retentionDays">Number of days to keep a log file before it is deleted.</param>
        private void CleanupOldLogs(string logDir, int retentionDays)
        {
            try
            {
                if (!Directory.Exists(logDir)) return;

                DateTime cutoff = DateTime.Now.AddDays(-retentionDays);
                foreach (var file in Directory.GetFiles(logDir, "uipath_python_*.txt"))
                {
                    if (File.GetCreationTime(file) < cutoff)
                    {
                        File.Delete(file);
                    }
                }
            }
            catch
            {
                // Intentionally ignored: a failure to clean up old logs should never
                // cause the Python invocation itself to fail.
            }
        }
    }
}