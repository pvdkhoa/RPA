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
        public UiPath.GSuite.Activities.Api.DriveConnection RPA_thanhtuyen_quintet_co_kr { get; set; }

        public DriveFactory(ICodedWorkflowsServiceContainer resolver)
        {
            RPA_thanhtuyen_quintet_co_kr = new UiPath.GSuite.Activities.Api.DriveConnection("f01b3f94-ea99-4205-b50e-1c8205d72612", resolver);
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
        public UiPath.GSuite.Activities.Api.GmailConnection RPA_thanhtuyen_quintet_co_kr { get; set; }

        public GmailFactory(ICodedWorkflowsServiceContainer resolver)
        {
            RPA_thanhtuyen_quintet_co_kr = new UiPath.GSuite.Activities.Api.GmailConnection("a4da268b-7fc3-4a63-b8ec-3028fc01713c", resolver);
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