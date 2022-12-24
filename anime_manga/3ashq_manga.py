from click import prompt
from access_web_methods import *
import re, time, os, sys
from csv import DictReader, DictWriter
import requests
from .access_web_methods import *

'''
system parameters shoul be like (name_of_manga chapter_number)
e.g. shingeki-no-kyojin 55
'''

exec_script = '''
jQuery(document).ready(function($){
	wp_manga_reporting = false;
	
	$(document).on( 'click', '#btn_flag_chapter', function(evt){
		
		if(confirm(wp_chapter_report.are_you_sure)){
			
			if(!wp_manga_reporting){
				wp_manga_reporting = true;
				
				var volSelect = $('.volume-select');

				var mangaHasVolume = volSelect.length > 0 ? true : false;

				var curVol = mangaHasVolume ? volSelect.val() : 0;

				var	curVolChapSelect = $('.selectpicker_chapter[for="volume-id-' + curVol + '"] .single-chapter-select');
				
				data = {manga: $('#btn_flag_chapter').attr('data-manga'), chapter: curVolChapSelect.val(), action: 'chapter_flag'};
				
				$.ajax({
					type : 'POST',
					url : manga.ajax_url,
					data : data,
					success : function( response ){
						obj = JSON.parse(response);
						wp_manga_reporting = false;
						alert(obj.message);
					},
					error : function(err){
						wp_manga_reporting = false;
						alert(err);
					}
				});
			}
		}
		
		return false;
	});
});
'''

try:
	manga_name = sys.argv[1]# to get command line parameters	
except:
	manga_name = input('Enter manga name: ')

url = 'https://3asq.org/manga/'

if not manga_name.strip() or requests.get(url+manga_name.strip()).status_code != 200:
	print('there is no manga with this name')
	exit()

if not os.path.exists(f'./{manga_name}'):
	os.mkdir(f'./{manga_name}')

os.chdir(f'./{manga_name}')

manga_chapters_links = {}
driver = None

if not os.path.exists(f'links.csv'):

	

	driver.get(url+manga_name)
	time.sleep(5)

	try:
		driver.execute_script(exec_script)
	except:
		print('cannot execute script to load chapters')
		exit()

	all_chapters = driver.find_elements_by_class_name('wp-manga-chapter')

	with open(f'links.csv', 'w') as csv_file:
		csv_file = open(f'links.csv', 'w')
		writer = DictWriter(csv_file, fieldnames=['name', 'link'])
		writer.writeheader()

		for tag in all_chapters:
			a_tag = tag.find_element_by_tag_name('a')
			href = a_tag.get_attribute('href')
			manga_chapters_links[a_tag.text] = href
			writer.writerow(rowdict={'name':a_tag.text, 'link':href})
	driver.close()
	print('driver closed')

else:
	print('links are restored from file')
	with open(f'links.csv') as csv_file:
		reader = DictReader(csv_file)
		for row in reader:
			manga_chapters_links[row['name']] = row['link']

print('there are',manga_chapters_links.__len__(),'chapters for this manga')
'''
if not driver:
	driver = webdriver.Firefox(executable_path="C:\driver\geckodriver.exe")
'''
try:
	chapter_num = eval(sys.argv[2])# to get command line parameters
except:
	chapter_num = prompt('Enter chapter number', type=eval)


for name, link in manga_chapters_links.items():
	'''
	if os.path.exists(f'{manga_name}/chapter-{name}.pdf'):
		continue
	'''
	if str(chapter_num) == re.search('([\d\.]+)', name)[0]:
		
		#driver.get(link)

		pdf_file = open(f'chapter-{name}.pdf', 'wb')

		print('chapter ',re.search('([\d\.]+)', name)[0], ' started')

		all_imgs = get_elements_by_attrs(url=link, tag='img', attrs={'class':'wp-manga-chapter-img'})#with beautifulsoup
		#all_imgs = driver.find_elements_by_class_name('wp-manga-chapter-img')

		if not all_imgs:
			pdf_file.close()
			os.remove(f'chapter-{name}.pdf')
			print('cannot get images')
			break
		
		print('there are', all_imgs.__len__(), 'images')
			
		content = get_content_of_imgs(all_imgs)#with bs4 and requests
		convert_imgs_list_into_pdf(content, pdf_file)
		#save_imgs_as_pdf(imgs=all_imgs, pdf_file=pdf_file)#with selenium and images

		break#if executed, else statement does not execute

else:#if loop finishes, but did not achieve if statement
	print('this chapter',chapter_num, 'does not exist')