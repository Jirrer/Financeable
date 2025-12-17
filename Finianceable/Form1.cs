using System.Diagnostics;

namespace Finianceable
{
    public partial class Form1 : Form
    {
        List<Panel> listPanel = new List<Panel>();
        int index;
        string selectedMonthYear;
        public Form1()
        {
            InitializeComponent();
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void label2_Click(object sender, EventArgs e)
        {

        }

        private void label3_Click(object sender, EventArgs e)
        {

        }

        private void button1_Click(object sender, EventArgs e)
        {
            index = 0;
            listPanel[index].BringToFront();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            index = 1;
            listPanel[index].BringToFront();

            selectedMonthYear = dateTimePicker1.Value.ToString();
        }

        private void button3_Click(object sender, EventArgs e)
        {
            index = 2;
            listPanel[index].BringToFront();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            listPanel.Add(panel1);
            listPanel.Add(panel2);
            listPanel.Add(panel3);

            index = 0;
            listPanel[index].BringToFront();

        }

        private void button4_Click(object sender, EventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog {
                Title = "Select a file",
                Filter = "CSV Files (*.csv)|*.csv",
                Multiselect = false
            };

            if (openFileDialog.ShowDialog() != DialogResult.OK)
                return;

            string sourceFile = openFileDialog.FileName;

            string exeDirectory = Application.StartupPath;

            string subFolder = Path.Combine(exeDirectory, "ReportData");

            Directory.CreateDirectory(subFolder);

            string destinationPath = Path.Combine(
                subFolder,
                Path.GetFileName(sourceFile)
            );

            File.Copy(sourceFile, destinationPath, overwrite: true);

            label4.Text += $"\n{sourceFile}";
        }

        private void dateTimePicker1_ValueChanged(object sender, EventArgs e)
        {
            selectedMonthYear = dateTimePicker1.Value.ToString();
        }

        private void button5_Click(object sender, EventArgs e)
        {
            DateTime selectedDate = dateTimePicker1.Value;
            string month = selectedDate.Month.ToString("00");
            string year = selectedDate.Year.ToString();

            string date = $"{month}/{year}";

            string venvPython = Path.Combine(Application.StartupPath, @"env\Scripts\python.exe");
            string scriptPath = Path.Combine(Application.StartupPath, @"GenerateData.py");
            string tag = "-delete";

            ProcessStartInfo psi = new ProcessStartInfo {
                FileName = venvPython,
                Arguments = $"\"{scriptPath}\" \"{date}\" \"{tag}\"",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            using (Process process = Process.Start(psi))
            {
                string output = process.StandardOutput.ReadToEnd();
                string errors = process.StandardError.ReadToEnd();
                process.WaitForExit();

                if (!string.IsNullOrEmpty(errors))
                {
                    MessageBox.Show("Errors:\n" + errors);
                }
                else
                {
                    MessageBox.Show("Ran Report");
                    label4.Text = string.Empty;
                }
            }
        }
    }
}
