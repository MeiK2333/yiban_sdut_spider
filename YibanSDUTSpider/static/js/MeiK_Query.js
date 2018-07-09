var placeholder = '喵';

$(function () {
	$(".ui.dropdown").dropdown({keepOnScreen: true});
	$(".card .retry-button").click(function () {
		var card = $(this).closest(".card");
		resetCard(card);
		loadCardData(card.data("id"));
	});
	$(".modal .retry-button").click(function () {
		var modal = $(this).closest(".modal");
		resetModal(modal);
		loadModalData(modal.data("id"));
	});
});

function showRetryButton(obj) {
	obj.find('.link-button').hide();
	obj.find(".retry-button").show();
}

function showLinkButton(obj, content, url) {
	obj.find('.retry-button').hide();
	obj.find(".link-button").show();
	obj.find(".link-button").attr("href", url);
        obj.find(".link-button").find('button').text(content);
}

function resetCard(card) {
	card.find(".dimmer").css("opacity", 1);
	card.find(".main-loader").css("opacity", 1);
	card.find(".cover-buttons").hide();
	card.find(".cover-buttons").css("opacity", 0);
	card.find(".main-header").css("opacity", 0);
	card.find(".main-extra").css("opacity", 0);
}

function resetModal(modal) {
	modal.find(".dimmer").css("opacity", 1);
	modal.find(".main-loader").css("opacity", 1);
	modal.find(".cover-buttons").hide();
	modal.find(".cover-buttons").css("opacity", 0);
	modal.find(".header").css("opacity", 0);
	modal.find(".close").css("opacity", 0);
	modal.find(".content").css("opacity", 0);
	modal.find(".actions").css("opacity", 0);
}

function loadCardData(item) {
	var card = $(dataCardClass[item]);
	card.find(".cover-buttons").hide();
	$.ajax({
		url: dataCardUrl[item],
		dataType: 'json',
		timeout: 10000,
		cache: false,
		success: function (res) {
			if(res["code"] == 0) {
				var data = res["data"];
				if(data["item"] == "") {
					card.find(".item").addClass("ghost");
					card.find(".item").text(placeholder);
				}
				else card.find(".item").text(data["item"]);
				if(data["value"] == "") {
					card.find(".value").addClass("ghost");
					card.find(".value").text(placeholder);
				}
				else card.find(".value").text(data["value"]);
				if(data["unit"] == "") {
					card.find(".unit").addClass("ghost");
					card.find(".unit").text(placeholder);
				}
				else card.find(".unit").text(data["unit"]);

				if(data["extra"]["type"] == 'link') {
					card.attr("data-type", 'link');
					card.attr("href", data["extra"]["url"]);
					card.click(function () {
						window.location.href = card.attr("href");
					});
				}
				if(data["extra"]["type"] == 'ajax') {
					card.attr("data-type", 'modal');
					dataModalUrl[item] = data["extra"]["url"];
					card.click(function () {
						$(".detail.modal[data-id='" + item + "']").modal('show');
						if(dataModalUrl[item] != '' && !dataModalInitialized[item])
							loadModalData(item);
					});
				}
				card.find(".dimmer").animate({"opacity": 0}, 250, function () {
					card.find(".main-header").animate({"opacity": 1}, 500);
					card.find(".main-extra").animate({"opacity": 1}, 500);
					card.find(".dimmer").hide();
				});
			}
			else {
				card.find(".main-loader").animate({"opacity": 0}, 250, function () {
					showLinkButton(card, res["msg"], res["data"]["url"]);
					card.find(".cover-buttons").show();
					card.find(".cover-buttons").animate({"opacity": 1}, 500);
				});
			}
		}, error: function () {
			card.find(".main-loader").animate({"opacity": 0}, 250, function () {
				showRetryButton(card);
				card.find(".cover-buttons").show();
				card.find(".cover-buttons").animate({"opacity": 1}, 500);
			});
		}
	});
}

function loadModalData(item) {
	dataModalInitialized[item] = true;
	var modal = $(dataModalClass[item]);
	modal.find(".cover-buttons").hide();
	$.ajax({
		url: dataModalUrl[item],
		dataType: 'json',
		timeout: 10000,
		cache: false,
		success: function (res) {
			dataModalUrl[item] = '';
			var type = res["type"];
			var data = res["data"];
			if(data.length == 0) {
				console.log('hre');
				modal.find(".no-data-text").show();
			}
			else {
				var tbody = modal.find("tbody");
				if(item == 0) { // 校园卡
					for(var i = 0; i < data.length; ++i) {
						tbody.append('<tr class="detail-header"></tr>');
						tbody.find("tr:last").append('<td rowspan="5" class="top aligned">' + data[i]["time"].substr(5) + '</td>');
						tbody.find("tr:last").append('<td class="right aligned top aligned">消费金额：</td>');
						tbody.find("tr:last").append('<td>' + data[i]["amount"] + ' 元</td>');
						tbody.append('<tr></tr>');
						tbody.find("tr:last").append('<td class="right aligned top aligned">余额：</td>');
						tbody.find("tr:last").append('<td>' + data[i]["balance"] + ' 元</td>');
						tbody.append('<tr></tr>');
						tbody.find("tr:last").append('<td class="right aligned top aligned">消费原因：</td>');
						tbody.find("tr:last").append('<td>' + data[i]["reason"] + '</td>');
						tbody.append('<tr></tr>');
						tbody.find("tr:last").append('<td class="right aligned top aligned">消费站点：</td>');
						tbody.find("tr:last").append('<td>' + data[i]["position"] + '</td>');
						tbody.append('<tr class="detail-footer"></tr>');
						tbody.find("tr:last").append('<td class="right aligned top aligned">刷卡终端：</td>');
						tbody.find("tr:last").append('<td>' + data[i]["termName"] + '</td>');
					}
				}
				if(item == 1) { // 宿舍电量
					var energy = parseFloat(data["energy"]);
					var remdMin = data['lower'];
					var remdMax = data['upper'];
					tbody.append('<tr></tr>');
					tbody.find("tr:last").append('<td class="right aligned top aligned detail-key">宿舍：</td>');
					tbody.find("tr:last").append('<td>' + data["room"] + '</td>');
					tbody.append('<tr></tr>');
					tbody.find("tr:last").append('<td class="right aligned top aligned detail-key">电量余量：</td>');
					tbody.find("tr:last").append('<td>' + data["energy"] + ' 度</td>');
					tbody.append('<tr></tr>');
					tbody.find("tr:last").append('<td class="right aligned top aligned detail-key">预计可用：</td>');
					tbody.find("tr:last").append('<td>' + remdMin + ' - ' + remdMax + ' 天</td>');
					tbody.append('<tr></tr>');
					tbody.find("tr:last").append('<td class="right aligned top aligned detail-key">更新时间：</td>');
					tbody.find("tr:last").append('<td>' + data["date"] + '</td>');
				}
				if(item == 3) { // 图书借阅
					for(var i = 0; i < data.length; ++i) {
						var daysRemd = Math.floor((new Date(data[i]["backDate"])-new Date())/(24*60*60*1000));
						tbody.append('<tr class="detail-header"></tr>');
						tbody.find("tr:last").append('<td rowspan="5" class="top aligned">' + data[i]["borrowDate"] + '</td>');
						tbody.find("tr:last").append('<td class="right aligned top aligned">书名：</td>');
						tbody.find("tr:last").append('<td>' + data[i]["title"] + '</td>');
						tbody.append('<tr></tr>');
						tbody.find("tr:last").append('<td class="right aligned top aligned">作者：</td>');
						tbody.find("tr:last").append('<td>' + data[i]["author"] + '</td>');
						tbody.append('<tr></tr>');
						tbody.find("tr:last").append('<td class="right aligned top aligned">借阅数量：</td>');
						tbody.find("tr:last").append('<td>' + data[i]["borrowCnt"] + '</td>');
						tbody.append('<tr></tr>');
						tbody.find("tr:last").append('<td class="right aligned top aligned">书籍属区：</td>');
						tbody.find("tr:last").append('<td>' + data[i]["site"] + '</td>');
						tbody.append('<tr class="detail-footer"></tr>');
						tbody.find("tr:last").append('<td class="right aligned top aligned">应还日期：</td>');
						if(daysRemd < 7)
							tbody.find("tr:last").append('<td>' + data[i]["backDate"] + ' <span class="ui transparent-black horizontal label">剩 ' + daysRemd +' 天</span></td>');
						else tbody.find("tr:last").append('<td>' + data[i]["backDate"] + '</td>');
					}
				}
			}

			modal.modal('refresh');
			modal.find(".dimmer").animate({"opacity": 0}, 250, function () {
				modal.find(".header").animate({"opacity": 1}, 500);
				modal.find(".close").animate({"opacity": 1}, 500);
				modal.find(".content").animate({"opacity": 1}, 500);
				modal.find(".actions").animate({"opacity": 1}, 500);
				modal.find(".dimmer").hide();
			});
		}, error: function () {
			modal.find(".main-loader").animate({"opacity": 0}, 250, function () {
				showRetryButton(modal);
				modal.find(".cover-buttons").show();
				modal.find(".cover-buttons").animate({"opacity": 1}, 500);
			});
		}
	});
}
