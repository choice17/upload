#include <json.h>
#include <stdio.h>
#include <string.h>
/* For compile, Please use for link the library on your own */
/* gcc parse_json.c -o app `pkg-config --cflags --libs json-c` */
#define VOID void
#define MAX_ZONE_NUM 6

typedef struct {
	char px; //Starting point x  [0-100]
	char py; //Starting point Y  [0-100]
	char w; //w    [0-100]
	char h; //h    [0-100]
} ZONE_S;

typedef struct {
	int zcnt; //Number of detection areas
	ZONE_S zone[MAX_ZONE_NUM];
} ZONE_LIST_S;


static VOID parse_zone_resp(struct json_object *obj, ZONE_LIST_S *zone_info)
{
	struct json_object *tmp_obj;
	struct json_object *tmp_obj0;
    struct json_object *tmp_obj1;
	int i, len, zone_num=0;
	char str[32];
    // "{\"num\":1,\"region0\":{\"x\":0,\"y\":0,\"xlen\":50,\"ylen\":50}}" 
    if (json_object_object_get_ex(obj, "num", &tmp_obj)) {
        zone_info->zcnt = json_object_get_int(tmp_obj);
        if (zone_info->zcnt >= MAX_ZONE_NUM) {
            zone_info->zcnt = MAX_ZONE_NUM;
            printf("zone number(%d) exceed Maximum number(%d)!\n", zone_info->zcnt, MAX_ALARM_ZONE_NUM);
            return;
        }
        zone_num = 0;
        for (i = 0; i < zone_info->zcnt; i++) {
            len = sprintf(str, "region%d", i);
            if (json_object_object_get_ex(obj, str, &tmp_obj)) {
                if (json_object_object_get_ex(tmp_obj, "x", &tmp_obj0))
                    zone_info->zone[zone_num].px = json_object_get_int(tmp_obj0);
                if (json_object_object_get_ex(tmp_obj, "y", &tmp_obj0))
                    zone_info->zone[zone_num].py = json_object_get_int(tmp_obj0);
                if (json_object_object_get_ex(tmp_obj, "xlen", &tmp_obj0))
                    zone_info->zone[zone_num].w = json_object_get_int(tmp_obj0);
                if (json_object_object_get_ex(tmp_obj, "ylen", &tmp_obj0))
                    zone_info->zone[zone_num].h = json_object_get_int(tmp_obj0);
                zone_num++;
            } else {
                continue;
            }
        }
    }

}

static VOID getZoneInfo(char *p_alarm_zone, ZONE_LIST_S *zone_info)
{
	int retval = 0;
	enum json_tokener_error jerr;
	struct json_object *json_obj = NULL;
	struct json_tokener *tok = json_tokener_new();
	json_obj = json_tokener_parse_ex(tok, p_alarm_zone, strlen(p_alarm_zone));

	jerr = json_tokener_get_error(tok);
	if (jerr == json_tokener_success) {
		parse_zone_resp(json_obj, zone_info);
		if (json_obj != NULL) {
			json_object_put(json_obj); //Decrement the ref count and free if it reaches zero
		} else {
			PR_DEBUG("empty json object parsed\n");
		}
	} else {
		PR_DEBUG(" JSON Tokener errNo: %d = %s \n\n", jerr, json_tokener_error_desc(jerr));
		retval = -1;
	}
	json_tokener_free(tok);
}

int main(void)
{
    char *msg = "{\"num\":1,\"region0\":{\"x\":0,\"y\":0,\"xlen\":50,\"ylen\":50}}";
    ZONE_LIST_S zone = {0};
    getZoneInfo(msg, &zone);
    printf("num:%d (%d,%d,%d,%d)\n", zone.zcnt, 
    zone.zone[0].px,
    zone.zone[0].py,
    zone.zone[0].w,
    zone.zone[0].h);
    return 0;
}
