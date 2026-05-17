# Copyright (C) 2026 | GamingonTour1 | All Rights Reserved
# Unauthorized copying, distributing, and using of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Lennox Matzerath (GamingonTour1) <gamingontour2016@gmail.com>

import re

def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")