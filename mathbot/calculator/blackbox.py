import asyncio
import calculator.interpereter
import calculator.parser
import calculator.runtime
import calculator.bytecode
import calculator.errors
import calculator.runtime


ERROR_TEMPLATE = '''\
On line {line_num} at position {position}
{prev}
{cur}
{carat}'''


class Terminal():

    def __init__(self, allow_special_commands = False):
        self.show_tree = False
        self.show_parsepoint = False
        self.builder = calculator.bytecode.CodeBuilder()
        self.allow_special_commands = allow_special_commands
        runtime = calculator.runtime.wrap_with_runtime(self.builder, None)
        self.interpereter = calculator.interpereter.Interpereter(runtime, builder = self.builder)
        self.interpereter.run()
        self.line_count = 0

    def execute(self, code):
        loop = asyncio.get_event_loop()
        future = self.execute_internal(code)
        return loop.run_until_complete(future)

    async def execute_async(self, code):
        return await self.execute_internal(code)

    async def execute_internal(self, line):
        ''' Runs some code.
            Returns a string-bool tuple.
            The string is the output to display to the user.
            The bool is True if nothing went wrong.
        '''
        output = []
        def prt(*args):
            output.append(' '.join(map(str, args)))
        self.line_count += 1
        worked = True
        if self.allow_special_commands and line == ':tree':
            show_tree = not show_tree
        elif self.allow_special_commands and line == ':parsepoint':
            show_parsepoint = not show_parsepoint
        elif self.allow_special_commands and line == ':trace':
            self.interpereter.trace = not self.interpereter.trace
        elif self.allow_special_commands and line == ':cache':
            for key, value in self.interpereter.calling_cache.values.items():
                prt('{:40} : {:20}'.format(str(key), str(value)))
        else:
            worked = False
            try:
                tokens, ast = calculator.parser.parse(line, source_name = 'iterm_' + str(self.line_count))
                if self.show_tree:
                    prt(json.dumps(ast, indent = 4))
                ast = {'#': 'program', 'items': [ast, {'#': 'end'}]}
                self.interpereter.prepare_extra_code({
                    '#': 'program',
                    'items': [ast]
                })
                # for index, byte in enumerate(bytes):
                #   print('{:3d} - {}'.format(index, byte))
                result = await asyncio.wait_for(self.interpereter.run_async(), 5)
                if result is not None:
                    prt(result)
                worked = True
            except calculator.errors.CompilationError as e:
                prt('Compilation error')
                prt(e.description)
                if e.position is not None:
                    prt(format_error_place(line, e.position))
            except calculator.errors.EvaluationError as e:
                dbg = e._linking
                if dbg is None:
                    prt('No debugging information available for this error.')
                    # prt('You may wish to open an issue: github.com/DXsmiley/mathbot')
                else:
                    prt('Runtime error in', dbg['name'])
                    prt(format_error_place(dbg['code'], dbg['position']))
                prt(str(e))
                # prt('-' * len(str(e)), '\n')
            except calculator.parser.ParseFailed as e:
                prt('Parse error')
                prt(format_error_place(line, e.position))
            except calculator.parser.TokenizationFailed as e:
                prt('Tokenization error')
                prt(format_error_place(line, e.position))
            except asyncio.TimeoutError:
                prt('Operation timed out')
            except Exception as e:
                traceback.print_exc()
                prt('Some other unknown error occurred')
        return '\n'.join(output), worked


def format_error_place(string, position):
    lines = [''] + string.split('\n') + ['']
    line = 1
    while line < len(lines) - 2 and position > len(lines[line]):
        position -= len(lines[line]) + 1
        line += 1
    return ERROR_TEMPLATE.format(
        line_num = line,
        position = position + 1,
        prev = lines[line - 1],
        cur = lines[line],
        next = lines[line + 1],
        carat = ' ' * position + '^'
    )
