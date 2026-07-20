"""Named references into fixtures/sample_data.json, so integration tests can read like prose
instead of scattering raw UUID strings.
"""

import uuid

ADA_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
ALAN_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
GRACE_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")

TASK_DESIGN_API_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")  # PLANNED, unassigned
TASK_IMPLEMENT_SERVICE_ID = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")  # ASSIGNED to Ada
TASK_WRITE_TESTS_ID = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")  # STARTED, assigned to Alan
TASK_SHIP_RELEASE_ID = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")  # DONE, assigned to Grace
