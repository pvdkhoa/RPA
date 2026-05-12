using UiPath.CodedWorkflows;
using System;

namespace REF_RPA
{
    public class GoogleDocsFactory
    {
        public GoogleDocsFactory(ICodedWorkflowsServiceContainer resolver)
        {
        }
    }

    public class DriveFactory
    {
        public DriveFactory(ICodedWorkflowsServiceContainer resolver)
        {
        }
    }

    public class GoogleFormsFactory
    {
        public GoogleFormsFactory(ICodedWorkflowsServiceContainer resolver)
        {
        }
    }

    public class GmailFactory
    {
        public UiPath.GSuite.Activities.Api.GmailConnection My_Workspace_20145393_student_hcmute_edu_vn { get; set; }

        public GmailFactory(ICodedWorkflowsServiceContainer resolver)
        {
            My_Workspace_20145393_student_hcmute_edu_vn = new UiPath.GSuite.Activities.Api.GmailConnection("c366934d-7fd1-4973-b886-a4fad4f6113e", resolver);
        }
    }

    public class GoogleSheetsFactory
    {
        public GoogleSheetsFactory(ICodedWorkflowsServiceContainer resolver)
        {
        }
    }

    public class GoogleTasksFactory
    {
        public GoogleTasksFactory(ICodedWorkflowsServiceContainer resolver)
        {
        }
    }

    public class GoogleWorkspaceFactory
    {
        public GoogleWorkspaceFactory(ICodedWorkflowsServiceContainer resolver)
        {
        }
    }
}