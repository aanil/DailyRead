import git
import os
import pytest
import json
from daily_read import ngi_data
from datetime import date, timedelta
import copy


dummy_order_open = {
    "orderer": "dummy@dummy.se",
    "project_dates": {
        "2023-06-15": ["Samples Received"],
        "2023-06-28": ["Reception Control finished", "Library QC finished"],
    },
    "internal_id": "P123456",
    "internal_name": "D.Dummysson_23_01",
}

dummy_order_closed = {
    "orderer": "dummy@dummy.se",
    "project_dates": {
        "2023-06-15": ["Samples Received"],
        "2023-06-28": ["Reception Control finished", "Library QC finished"],
        "2023-07-28": ["All Samples Sequenced"],
        "2023-07-29": ["All Raw data Delivered"],
    },
    "internal_id": "P123456",
    "internal_name": "D.Dummysson_23_01",
}

order_portal_resp_order_processing = {
    "identifier": "NGI123456",
    "title": "Test run with nano",
    "iuid": "2b896d9fb38349d0b04943f345efq123",
    "form": {
        "iuid": "63c21673c16c4034120277d809dcd577",
        "title": "Illumina Sequencing",
        "version": "2023-09-01",
        "links": {"api": {"href": "https://orderportal.example.com/orders/form/63c21673c16c4034120277d809dcd577"}},
    },
    "owner": {
        "email": "dummy@dummy.se",
        "name": "Dummysson, Dummy",
        "links": {
            "api": {"href": "https://orderportal.example.com/orders/api/v1/account/dummy%40dummy.se"},
            "display": {"href": "https://orderportal.example.com/orders/account/dummy%40dummy.se"},
        },
    },
    "status": "processing",
    "reports": [],
    "history": {
        "preparation": "2023-12-06",
        "submitted": "2023-12-06",
        "review": "2023-12-06",
        "accepted": "2023-12-06",
        "rejected": None,
        "processing": "2023-12-20",
        "aborted": None,
        "closed": None,
        "undefined": None,
    },
    "tags": [],
    "modified": "2023-12-20T02:30:49.541Z",
    "created": "2023-12-06T10:15:11.081Z",
    "links": {
        "api": {"href": "https://orderportal.example.com/orders/api/v1/order/NGI123456"},
        "display": {"href": "https://orderportal.example.com/orders/order/NGI123456"},
    },
    "fields": {
        "assigned_node": "Stockholm",
        "project_ngi_identifier": "P123456",
        "project_ngi_name": "D.Dummysson_23_01",
    },
}

order_portal_resp_order_processing_mult_reports = copy.deepcopy(order_portal_resp_order_processing)

order_portal_resp_order_processing_mult_reports["identifier"] = "NGI123454"
order_portal_resp_order_processing_mult_reports["reports"] = [
    {
        "iuid": "c5ee942",
        "name": "Project Progress",
        "filename": "project_progress.html",
        "status": "published",
        "modified": "2023-12-28T15:09:18.732Z",
        "links": {
            "api": {"href": "https://orderportal.example.com/orders/api/v1/report/c5ee942"},
            "file": {"href": "https://orderportal.example.com/orders/report/c5ee942"},
        },
    },
    {
        "iuid": "c5ee941",
        "name": "Project Progress",
        "filename": "project_progress.html",
        "status": "published",
        "modified": "2023-12-28T15:09:18.732Z",
        "links": {
            "api": {"href": "https://orderportal.example.com/orders/api/v1/report/c5ee941"},
            "file": {"href": "https://orderportal.example.com/orders/report/c5ee941"},
        },
    },
]

order_portal_resp_order_closed = {
    "identifier": "NGI123455",
    "title": "Test run with closed",
    "iuid": "2b896d9fb38349d0b04943f345123123",
    "form": {
        "iuid": "12321673c16c4034120277d809dcd577",
        "title": "Illumina Sequencing",
        "version": "2023-09-01",
        "links": {"api": {"href": "https://orderportal.example.com/orders/form/12321673c16c4034120277d809dcd577"}},
    },
    "owner": {
        "email": "dummy@dummy.se",
        "name": "Dummysson, Dummy",
        "links": {
            "api": {"href": "https://orderportal.example.com/orders/api/v1/account/dummy%40dummy.se"},
            "display": {"href": "https://orderportal.example.com/orders/account/dummy%40dummy.se"},
        },
    },
    "status": "closed",
    "reports": [],
    "history": {
        "preparation": "2023-07-06",
        "submitted": "2023-07-06",
        "review": "2023-07-06",
        "accepted": "2023-07-06",
        "rejected": None,
        "processing": "2023-07-20",
        "aborted": None,
        "closed": (date.today() - timedelta(days=31)).strftime("%Y-%m-%d"),
        "undefined": None,
    },
    "tags": [],
    "modified": "2023-12-20T02:30:49.541Z",
    "created": "2023-07-06T10:15:11.081Z",
    "links": {
        "api": {"href": "https://orderportal.example.com/orders/api/v1/order/NGI123455"},
        "display": {"href": "https://orderportal.example.com/orders/order/NGI123455"},
    },
    "fields": {
        "assigned_node": "Stockholm",
        "project_ngi_identifier": "P123455",
        "project_ngi_name": "D.Dummysson_23_01",
    },
}


def _create_all_files(file_list, data_location):
    """Helper method to create files in file_list inside data_location"""
    for file_relpath in file_list:
        file_path = os.path.join(data_location, file_relpath)
        os.makedirs(os.path.split(file_path)[0], exist_ok=True)
        with open(file_path, "w") as fh:
            fh.write(json.dumps(dummy_order_open))


####################################################### FIXTURES #########################################################


@pytest.fixture
def data_repo(tmp_path):
    data_location = os.path.join(tmp_path, "git_repo")
    os.environ["DAILY_READ_DATA_LOCATION"] = str(data_location)
    os.mkdir(data_location)
    data_repo = git.Repo.init(data_location)

    # Need an empty commit to be able to do "repo.index.diff("HEAD")"
    new_file_path = os.path.join(data_location, ".empty")
    open(new_file_path, "a").close()
    data_repo.index.add([new_file_path])
    data_repo.index.commit("Empty file from tests as a first commit")

    return data_repo


@pytest.fixture
def data_repo_no_commit(tmp_path):
    data_location = os.path.join(tmp_path, "git_repo")
    os.environ["DAILY_READ_DATA_LOCATION"] = str(data_location)
    os.mkdir(data_location)
    data_repo = git.Repo.init(data_location)
    return data_repo


@pytest.fixture
def data_repo_untracked(data_repo):
    """Adds two untracked files."""
    untracked_files = ["NGIS/2023/untracked_file1.json", "UGC/2022/untracked_file2.json"]
    _create_all_files(untracked_files, data_repo.working_dir)

    return data_repo


@pytest.fixture
def data_repo_new_staged(data_repo):
    """Adds two new files to the index to be committed."""
    staged_files = ["NGIS/2023/staged_file1.json", "UGC/2023/staged_file2.json", "NGIS/2023/staged_file2.json"]
    _create_all_files(staged_files, data_repo.working_dir)
    data_repo.index.add(staged_files)

    return data_repo


@pytest.fixture
def data_repo_modified_not_staged(data_repo):
    """Adds two previously committed files with new modifications that is not staged to be committed."""
    modified_not_staged_files = ["SNPSEQ/2023/modified_file1.json", "NGIS/2021/modified_file2.json"]
    _create_all_files(modified_not_staged_files, data_repo.working_dir)
    data_repo.index.add(modified_not_staged_files)
    # Check that nothing else is committed by mistake
    assert len(data_repo.index.diff("HEAD")) == len(modified_not_staged_files)
    data_repo.index.commit("Commit Message")

    for file_relpath in modified_not_staged_files:
        file_path = os.path.join(data_repo.working_dir, file_relpath)
        with open(file_path) as fh:
            json_list = json.load(fh)
        json_list["project_dates"].update({"2023-07-09": ["All Samples Sequenced"]})
        with open(file_path, "w") as fh:
            fh.write(json.dumps(json_list))

    return data_repo


@pytest.fixture
def data_repo_modified_staged(data_repo):
    """Adds two previously committed files with new modifications that is staged to be committed."""
    modified_not_staged_files = ["SNPSEQ/2022/modified_staged_file1.json", "NGIS/2020/modified_staged_file2.json"]
    _create_all_files(modified_not_staged_files, data_repo.working_dir)
    data_repo.index.add(modified_not_staged_files)
    data_repo.index.commit("Commit Message")

    for file_relpath in modified_not_staged_files:
        file_path = os.path.join(data_repo.working_dir, file_relpath)
        with open(file_path) as fh:
            json_list = json.load(fh)
        json_list["project_dates"].update({"2023-07-09": ["All Samples Sequenced"]})
        with open(file_path, "w") as fh:
            fh.write(json.dumps(json_list))

    return data_repo


@pytest.fixture
def data_repo_tracked(data_repo):
    """Adds three tracked files to the repository"""
    tracked_files = ["SNPSEQ/2022/tracked_file1.json", "UGC/2022/tracked_file2.json", "NGIS/2021/tracked_file3.json"]
    _create_all_files(tracked_files, data_repo.working_dir)
    data_repo.index.add(tracked_files)
    # Make sure nothing else is committed by mistake
    assert len(data_repo.index.diff("HEAD")) == len(tracked_files)
    data_repo.index.commit("Commit Message")

    return data_repo


@pytest.fixture
def data_repo_full(
    data_repo_untracked,
    data_repo_modified_not_staged,
    data_repo_tracked,
    data_repo_modified_staged,
    data_repo_new_staged,
):
    """Represents a data repository with all five different kinds of files.

    Note that the order of the fixtures matter since commits cannot be made if staged files exist.
    So files are staged in the final fixtures only.
    """
    return data_repo_new_staged


@pytest.fixture
def mock_project_data_record():
    def _method(status):
        if status == "open":
            mock_record = ngi_data.ProjectDataRecord(
                "NGIS/2023/staged_file1.json",
                dummy_order_open["orderer"],
                dummy_order_open["project_dates"],
                dummy_order_open["internal_id"],
                dummy_order_open["internal_name"],
            )
        if status == "closed":
            mock_record = ngi_data.ProjectDataRecord(
                "NGIS/2023/staged_file2.json",
                dummy_order_closed["orderer"],
                dummy_order_closed["project_dates"],
                dummy_order_closed["internal_id"],
                dummy_order_closed["internal_name"],
            )
        return mock_record

    return _method


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == "api/v1/orders":
        return MockResponse(
            {
                "items": [
                    order_portal_resp_order_processing,
                    order_portal_resp_order_closed,
                    order_portal_resp_order_processing_mult_reports,
                ]
            },
            200,
        )

    return MockResponse(None, 404)
